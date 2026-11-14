import datetime

from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, UniqueConstraint, JSON
from typing import List
from sqlalchemy import JSON as SQLJSON
from sqlalchemy.orm import mapped_column,Mapped
from database import Base
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

#phase should be added to the documentation log to track re-occurring symptoms for a particular phase

class DocumentationLog(Base):
    __tablename__ = "documentation_log"
    #__table_args__ = (UniqueConstraint("user_id","cycle_history_id"),)

    id =Column(String, primary_key=True, default= lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    cycle_history_id = Column(String, ForeignKey("cycle_history.id"), index=True, nullable=False)
    is_period = Column(Boolean,default=False)
    moods = Column(JSON, nullable=False, default=list)
    flow_intensity = Column(String, default=None,nullable=True)
    symptoms : Mapped[List[str]] = mapped_column(SQLJSON)
    phase = Column(String)
    other_symptoms = Column(String, nullable=True)
    created_at = Column(DateTime, default= lambda:datetime.now(timezone.utc))
    user = relationship("User", back_populates="document_logs")
    cycle_history = relationship("CycleHistory", back_populates="document_logs")
