import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from datetime import datetime
from .database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    work_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)  # accepted / revision_needed
    remarks = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
