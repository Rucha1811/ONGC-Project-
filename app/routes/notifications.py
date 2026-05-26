from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.base import Notification, User
from app.auth.deps import get_current_user
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list)
async def list_notifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id))
    return result.scalars().all()

@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id))
    notification = result.scalar_one_or_none()
    if not notification:
        return {"success": False}
    notification.is_read = True
    await db.commit()
    return {"success": True}
