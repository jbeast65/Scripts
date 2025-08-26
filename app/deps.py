from datetime import datetime, timezone
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Header, Request
from jose import jwt, JWTError

from .config import settings
from .schemas import User


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
	if not authorization:
		return None
	parts = authorization.split()
	if len(parts) == 2 and parts[0].lower() == "bearer":
		return parts[1]
	return None


def get_current_user(request: Request, authorization: Annotated[Optional[str], Header(default=None)] = None) -> User:
	# Try Authorization header first
	token = _extract_bearer_token(authorization)
	# Fallback to cookie
	if not token:
		token = request.cookies.get("access_token")
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		exp = payload.get("exp")
		if exp is not None and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
		user = User(
			id=str(payload.get("sub")),
			email=payload.get("email"),
			name=payload.get("name"),
			picture=payload.get("picture"),
		)
		return user
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")