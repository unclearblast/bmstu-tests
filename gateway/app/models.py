from pydantic import BaseModel
from typing import Optional

class WorkResponse(BaseModel):
    work_id: str
    student_name: str
    file_path: str
    created_at: str

class ReportResponse(BaseModel):
    report_id: str
    work_id: str
    status: str
    remarks: str
    created_at: str

class UploadResponse(BaseModel):
    work_id: str
    analysis_status: str
    message: str
