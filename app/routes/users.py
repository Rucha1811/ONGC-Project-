from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.base import User, Role
from app.schemas.base import User as UserSchema, UserCreate
from app.auth.deps import get_current_admin_user
from app.auth.security import hash_password
from uuid import uuid4

router = APIRouter()

@router.get("/", response_model=list[UserSchema])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin_user)):
    result = await db.execute(select(Role).where(Role.id == user.role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")
    db_user = User(
        id=uuid4(),
        cpf=user.cpf,
        password_hash=hash_password(user.password),
        name=user.name,
        designation=user.designation,
        section=user.section,
        level=user.level,
        is_active=user.is_active,
        role_id=user.role_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
