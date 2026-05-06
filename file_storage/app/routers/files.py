import shutil
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Work
from ..settings import UPLOAD_DIR

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
async def upload(
    student_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Сохраняем файл
    file_id = str(__import__('uuid').uuid4())
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Запись в БД
    work = Work(
        student_name=student_name,
        file_path=save_path
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    return {
        "work_id": work.id,
        "student_name": work.student_name,
        "file_path": work.file_path,
        "created_at": work.created_at.isoformat()
    }

@router.get("/{work_id}")
async def download(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    if not os.path.exists(work.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(work.file_path, media_type="application/octet-stream", filename=os.path.basename(work.file_path))
