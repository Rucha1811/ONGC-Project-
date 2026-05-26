from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.base import File, Approval, User
from app.schemas.base import Approval as ApprovalSchema, ApprovalCreate
from app.auth.deps import get_current_user
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.post("/approve/{file_id}", response_model=ApprovalSchema)
async def approve_file(file_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only admin or ops_manager can approve
    if current_user.role.name not in ["admin", "ops_manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    file.status = "Approved"
    approval = Approval(
        id=uuid4(),
        file_id=file.id,
        action="approved",
        action_by=current_user.id,
        action_at=datetime.utcnow(),
        comment="Approved by user"
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval

@router.post("/reject/{file_id}", response_model=ApprovalSchema)
async def reject_file(file_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only admin or ops_manager can reject
    if current_user.role.name not in ["admin", "ops_manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    file.status = "Rejected"
    approval = Approval(
        id=uuid4(),
        file_id=file.id,
        action="rejected",
        action_by=current_user.id,
        action_at=datetime.utcnow(),
        comment="Rejected by user"
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval
