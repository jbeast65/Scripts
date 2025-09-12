from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_session
from .db_models import User


security = HTTPBearer(auto_error=False)


def create_jwt(user_id: int) -> str:
    settings = get_settings()
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(lambda: get_session().__enter__()),  # type: ignore[misc]
):
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = creds.credentials
    settings = get_settings()
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id = int(data.get("sub"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def verify_google_id_token(id_token: str) -> dict:
    settings = get_settings()
    try:
        info = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            audience=settings.google_client_id if settings.google_client_id else None,
        )
        return info
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=f"Google token invalid: {exc}") from exc

