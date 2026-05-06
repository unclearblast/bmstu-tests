from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Report
from ..analysis import download_file_for_analysis, analyze_file
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze")
async def analyze_work(payload: dict, db: Session = Depends(get_db)):
    work_id = payload.get("work_id")
    if not work_id:
        raise HTTPException(status_code=400, detail="work_id is required")

    # Получаем файл из File Storage
    try:
        file_bytes = await download_file_for_analysis(work_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cannot retrieve file: {e}")

    # Анализируем (имя файла можно извлечь из заголовков ответа, но для простоты придумаем)
    filename = f"work_{work_id}.unknown"  # в реальности нужно передавать имя, но для MVP ОК
    result = analyze_file(filename, file_bytes)

    # Сохраняем отчёт
    report = Report(
        work_id=work_id,
        status=result["status"],
        remarks=result["remarks"]
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"report_id": report.id, "status": report.status, "remarks": report.remarks}

@router.get("/works/{work_id}/reports")
async def get_reports(work_id: str, db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.work_id == work_id).all()
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")
    return [{"report_id": r.id, "work_id": r.work_id, "status": r.status,
             "remarks": r.remarks, "created_at": r.created_at.isoformat()} for r in reports]
