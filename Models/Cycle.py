from database import Base
from sqlalchemy import Column, DateTime, String, ForeignKey,Integer
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
class Cycle(Base):
    __tablename__ = "cycle"

    id = Column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_day_last_period = Column(DateTime, nullable=False)
    cycle_length = Column(Integer, nullable=False)
    period_duration = Column(Integer, nullable=False)
    created_at = Column(DateTime, default= lambda : datetime.now(timezone.utc))
    user = relationship("User", back_populates="cycle")