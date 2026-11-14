import uuid

from database import Base
from sqlalchemy import Column, String,Integer, DateTime
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=False, default="Female")
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=True)
    google_sub = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, nullable=False, default="User")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    cycle = relationship("Cycle", back_populates="user")
    period_logs = relationship("PeriodLog", back_populates="user")
    document_logs = relationship("DocumentationLog", back_populates="user")
    cycle_history = relationship("CycleHistory", back_populates="user")

