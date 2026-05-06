import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analysis.db")
FILE_STORAGE_URL = os.getenv("FILE_STORAGE_URL", "http://file-storage:8000")
