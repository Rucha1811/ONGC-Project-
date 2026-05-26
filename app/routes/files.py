from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from app.database import get_db
from app.models.base import File, User
from app.schemas.base import File as FileSchema
from app.auth.deps import get_current_user
from uuid import uuid4
import os
from app.config import settings
from datetime import datetime

router = APIRouter()

@router.post("/upload", response_model=FileSchema)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    file_name: str = Form(...),
    file_type: str = Form(...),
    project_name: str = Form(None),
    sig_number: str = Form(None),
    data_type: str = Form(None),
    section: str = Form(None),
    category: str = Form(None),
    season: str = Form(None),
    block: str = Form(None),
    ml_block: str = Form(None),
    location: str = Form(None),
    classification: str = Form(None),
    file_size: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_ext = {"pdf","docx","xlsx","ppt","txt","dat","csv","zip"}
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="File type not allowed")
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_id = str(uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    db_file = File(
        id=file_id,
        file_name=file_name,
        file_type=file_type,
        project_name=project_name,
        sig_number=sig_number,
        data_type=data_type,
        section=section,
        category=category,
        season=season,
        block=block,
        ml_block=ml_block,
        location=location,
        classification=classification,
        status="Pending",
        uploaded_by=current_user.id,
        upload_date=datetime.utcnow(),
        file_size=file_size or str(os.path.getsize(file_path)),
        file_path=file_path
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    return db_file

@router.get("/", response_model=list[FileSchema])
async def list_files(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(File))
    return result.scalars().all()

@router.get("/download/{file_id}")
async def download_file(file_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file.file_path, filename=file.file_name, media_type="application/octet-stream")

@router.get("/search", response_model=list[FileSchema])
async def search_files(
    search: str = None,
    status: str = None,
    section: str = None,
    file_type: str = None,
    data_type: str = None,
    season: str = None,
    block: str = None,
    classification: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(File)
    filters = []
    if search:
        s = f"%{search.lower()}%"
        filters.append(or_(
            File.file_name.ilike(s),
            File.project_name.ilike(s),
            File.sig_number.ilike(s),
            File.category.ilike(s),
            File.location.ilike(s)
        ))
    if status:
        filters.append(File.status == status)
    if section:
        filters.append(File.section == section)
    if file_type:
        filters.append(File.file_type == file_type)
    if data_type:
        filters.append(File.data_type == data_type)
    if season:
        filters.append(File.season == season)
    if block:
        filters.append(File.block == block)
    if classification:
        filters.append(File.classification == classification)
    if filters:
        query = query.where(and_(*filters))
    result = await db.execute(query)
    return result.scalars().all()
