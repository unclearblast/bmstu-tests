import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .database import Base

class Work(Base):
    __tablename__ = "works"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
