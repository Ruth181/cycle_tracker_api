import datetime

from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from typing import List
from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column,Mapped
from database import Base
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class DocumentationLog(Base):
    __tablename__ = "documentation_log"
    id =Column(String, primary_key=True, default= lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    is_period = Column(Boolean,default=False)
    flow_intensity = Column(String, default=None,nullable=True)
    symptoms : Mapped[List[str]] = mapped_column(JSON)
    other_symptoms = Column(String, nullable=True)
    created_at = Column(DateTime, default= lambda:datetime.now(timezone.utc))
    user = relationship("User", back_populates="document_logs")
