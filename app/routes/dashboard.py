from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.base import File, User
from app.auth.deps import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Total, approved, pending, rejected
    result = await db.execute(select(File))
    files = result.scalars().all()
    total = len(files)
    approved = len([f for f in files if f.status == "Approved"])
    pending = len([f for f in files if f.status == "Pending"])
    rejected = len([f for f in files if f.status == "Rejected"])
    by_section = {}
    by_type = {}
    by_classification = {}
    for f in files:
        by_section[f.section] = by_section.get(f.section, 0) + 1 if f.section else 0
        by_type[f.file_type] = by_type.get(f.file_type, 0) + 1 if f.file_type else 0
        by_classification[f.classification] = by_classification.get(f.classification, 0) + 1 if f.classification else 0
    recent_activity = sorted(files, key=lambda x: x.upload_date or x.created_at, reverse=True)[:5]
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "bySection": by_section,
        "byType": by_type,
        "byClassification": by_classification,
        "recentActivity": [
            {
                "id": f.id,
                "fileName": f.file_name,
                "section": f.section,
                "category": f.category,
                "uploadedByName": str(f.uploaded_by),
                "uploadDate": f.upload_date,
                "status": f.status
            } for f in recent_activity
        ]
    }
