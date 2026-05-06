import httpx
from fastapi import HTTPException, status
from ..models import WorkResponse, ReportResponse

FILE_STORAGE_URL = "http://file-storage:8000"
ANALYSIS_URL = "http://file-analysis:8000"

async def upload_file(student_name: str, file_content: bytes, filename: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"file": (filename, file_content)}
        data = {"student_name": student_name}
        try:
            resp = await client.post(f"{FILE_STORAGE_URL}/files", data=data, files=files)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"File storage service error: {e}")

async def trigger_analysis(work_id: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(f"{ANALYSIS_URL}/analyze", json={"work_id": work_id})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"Analysis service error: {e}")

async def get_reports(work_id: str) -> list[ReportResponse]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{ANALYSIS_URL}/works/{work_id}/reports")
            resp.raise_for_status()
            return [ReportResponse(**r) for r in resp.json()]
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"Analysis service error: {e}")

async def get_wordcloud(work_id: str) -> bytes:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{ANALYSIS_URL}/works/{work_id}/wordcloud")
            resp.raise_for_status()
            return resp.content
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"Analysis service error: {e}")
