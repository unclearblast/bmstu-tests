from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import io

from ..services.service_clients import (
    upload_file,
    trigger_analysis,
    get_reports,
    get_wordcloud
)
from ..models import UploadResponse, ReportResponse

router = APIRouter()

@router.post("", response_model=UploadResponse)
async def submit_work(
    student_name: str = Form(...),
    file: UploadFile = File(...)
):
    # Сохраняем файл через File Storage Service
    content = await file.read()
    storage_resp = await upload_file(student_name, content, file.filename)
    work_id = storage_resp["work_id"]

    # Инициируем анализ
    analysis_resp = await trigger_analysis(work_id)

    return UploadResponse(
        work_id=work_id,
        analysis_status=analysis_resp.get("status", "unknown"),
        message=f"Work uploaded and analysis completed: {analysis_resp.get('remarks', '')}"
    )

@router.get("/{work_id}/reports", response_model=List[ReportResponse])
async def fetch_reports(work_id: str):
    reports = await get_reports(work_id)
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")
    return reports

@router.get("/{work_id}/wordcloud")
async def fetch_wordcloud(work_id: str):
    image_bytes = await get_wordcloud(work_id)
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
