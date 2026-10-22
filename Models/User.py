import uuid

from database import Base
from sqlalchemy import Column, String,Integer, DateTime, ForeignKey
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="User")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    cycle = relationship("Cycle", back_populates="user")

