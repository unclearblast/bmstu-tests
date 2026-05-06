import os
import httpx
from .settings import FILE_STORAGE_URL

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]
MAX_SIZE = 1 * 1024 * 1024  # 1 Мбайт

async def download_file_for_analysis(work_id: str) -> bytes:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{FILE_STORAGE_URL}/files/{work_id}")
        resp.raise_for_status()
        return resp.content

def analyze_file(filename: str, file_content: bytes) -> dict:
    ext = os.path.splitext(filename)[1].lower()
    remarks = []
    if ext not in ALLOWED_EXTENSIONS:
        remarks.append(f"Unsupported format: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    elif ext == ".zip":
        remarks.append("ZIP archives are not allowed")

    size = len(file_content)
    if size > MAX_SIZE:
        remarks.append(f"File size {size} bytes exceeds limit {MAX_SIZE} bytes")
    elif size == 0:
        remarks.append("File is empty")

    if not remarks:
        status = "accepted"
        remarks.append("All checks passed")
    else:
        status = "revision_needed"

    return {"status": status, "remarks": "; ".join(remarks)}
