import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from file_analysis.app.database import Base
from file_analysis.app.main import app
import os, io

TEST_DB = "sqlite:///./test_analysis.db"
os.environ["DATABASE_URL"] = TEST_DB

from file_analysis.app.database import engine, SessionLocal
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal.configure(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def fake_file_content(*args, **kwargs):
    # для тестов возвращаем маленький txt
    return b"Hello World"

def fake_file_content_invalid():
    return b"x" * 2_000_000  # > 1 MB

def test_analyze_success(monkeypatch):
    # подменяем функцию загрузки файла
    monkeypatch.setattr("file_analysis.app.routers.analysis.download_file_for_analysis", lambda x: fake_file_content())
    payload = {"work_id": "123"}
    resp = client.post("/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "accepted"

def test_analyze_oversized(monkeypatch):
    monkeypatch.setattr("file_analysis.app.routers.analysis.download_file_for_analysis", lambda x: fake_file_content_invalid())
    payload = {"work_id": "456"}
    resp = client.post("/analyze", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "revision_needed"
    assert "size" in resp.json()["remarks"]

def test_get_reports(monkeypatch):
    monkeypatch.setattr("file_analysis.app.routers.analysis.download_file_for_analysis", lambda x: b"test")
    # создадим отчет
    client.post("/analyze", json={"work_id": "789"})
    resp = client.get("/works/789/reports")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["work_id"] == "789"

def test_wordcloud(monkeypatch):
    monkeypatch.setattr("file_analysis.app.routers.wordcloud.download_file_for_analysis", lambda x: b"data science is awesome")
    resp = client.get("/works/abc/wordcloud")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
