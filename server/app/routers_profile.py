from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import get_current_user
from .db import get_session
from .db_models import Autotext, User


router = APIRouter(prefix="/v1/profile", tags=["profile"])


class AutotextIn(BaseModel):
    trigger: str
    expansion: str


class AutotextOut(BaseModel):
    id: int
    trigger: str
    expansion: str

    class Config:
        from_attributes = True


@router.get("/autotexts", response_model=List[AutotextOut])
def list_autotexts(
    user: User = Depends(get_current_user),
    db: Session = Depends(lambda: get_session().__enter__()),  # type: ignore[misc]
):
    result = db.execute(select(Autotext).where(Autotext.user_id == user.id).order_by(Autotext.trigger))
    return [AutotextOut.model_validate(row[0]) for row in result]


@router.post("/autotexts", response_model=AutotextOut)
def create_autotext(
    payload: AutotextIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(lambda: get_session().__enter__()),  # type: ignore[misc]
):
    exists = db.execute(
        select(Autotext).where(Autotext.user_id == user.id, Autotext.trigger == payload.trigger)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Trigger already exists")
    item = Autotext(user_id=user.id, trigger=payload.trigger.lower(), expansion=payload.expansion)
    db.add(item)
    db.flush()
    return AutotextOut.model_validate(item)


@router.put("/autotexts/{autotext_id}", response_model=AutotextOut)
def update_autotext(
    autotext_id: int,
    payload: AutotextIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(lambda: get_session().__enter__()),  # type: ignore[misc]
):
    item = db.get(Autotext, autotext_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    item.trigger = payload.trigger.lower()
    item.expansion = payload.expansion
    db.add(item)
    db.flush()
    return AutotextOut.model_validate(item)


@router.delete("/autotexts/{autotext_id}")
def delete_autotext(
    autotext_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(lambda: get_session().__enter__()),  # type: ignore[misc]
):
    item = db.get(Autotext, autotext_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    return {"ok": True}

