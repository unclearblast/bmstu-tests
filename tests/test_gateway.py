import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from gateway.app.main import app
from io import BytesIO

client = TestClient(app)

def test_submit_work_success():
    with patch("gateway.app.routers.works.upload_file", new_callable=AsyncMock) as mock_upload, \
         patch("gateway.app.routers.works.trigger_analysis", new_callable=AsyncMock) as mock_analysis:
        mock_upload.return_value = {"work_id": "1", "student_name": "Ivan", "file_path": "path", "created_at": "now"}
        mock_analysis.return_value = {"status": "accepted", "remarks": "OK"}

        resp = client.post("/works", data={"student_name": "Ivan"}, files={"file": ("test.txt", BytesIO(b"data"))})
        assert resp.status_code == 200
        json = resp.json()
        assert json["work_id"] == "1"
        assert json["analysis_status"] == "accepted"

def test_submit_work_storage_error():
    with patch("gateway.app.routers.works.upload_file", new_callable=AsyncMock) as mock_upload:
        mock_upload.side_effect = Exception("Storage down")
        resp = client.post("/works", data={"student_name": "Ivan"}, files={"file": ("test.txt", BytesIO(b"data"))})
        assert resp.status_code == 502
        assert "File storage service error" in resp.json()["detail"]

def test_get_reports():
    with patch("gateway.app.routers.works.get_reports", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [{"report_id": "r1", "work_id": "1", "status": "accepted", "remarks": "OK", "created_at": "2023-01-01"}]
        resp = client.get("/works/1/reports")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

def test_get_wordcloud():
    with patch("gateway.app.routers.works.get_wordcloud", new_callable=AsyncMock) as mock_wc:
        mock_wc.return_value = b"PNG_IMAGE_DATA"
        resp = client.get("/works/1/wordcloud")
        assert resp.status_code == 200
        assert resp.content == b"PNG_IMAGE_DATA"
