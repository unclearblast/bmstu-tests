import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from file_storage.app.database import Base
from file_storage.app.main import app
from file_storage.app.settings import UPLOAD_DIR
import os, shutil

TEST_DB = "sqlite:///./test_storage.db"
os.environ["DATABASE_URL"] = TEST_DB
os.environ["UPLOAD_DIR"] = "test_uploads"

# пересоздаём engine
from file_storage.app.database import engine, SessionLocal
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal.configure(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around():
    # очистка БД и папки перед каждым тестом
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)

def test_upload_file():
    files = {"file": ("test.txt", b"Hello World")}
    data = {"student_name": "Ivan"}
    resp = client.post("/files", data=data, files=files)
    assert resp.status_code == 200
    json = resp.json()
    assert json["student_name"] == "Ivan"
    assert "work_id" in json
    assert json["file_path"].endswith(".txt")

def test_download_file():
    # сначала загрузим
    files = {"file": ("test.txt", b"Hello World")}
    data = {"student_name": "Ivan"}
    resp = client.post("/files", data=data, files=files)
    work_id = resp.json()["work_id"]
    resp_get = client.get(f"/files/{work_id}")
    assert resp_get.status_code == 200
    assert resp_get.content == b"Hello World"

def test_download_nonexistent():
    resp = client.get("/files/nonexistent")
    assert resp.status_code == 404
