from database import Base
from sqlalchemy import Column, String, ForeignKey, DateTime
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class PeriodLog(Base):
    __tablename__ = "period_log"
    id = Column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda:datetime.now(timezone.utc), nullable=False)
    user = relationship("User", back_populates="period_logs")
