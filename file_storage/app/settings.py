import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./file_storage.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
