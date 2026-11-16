from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint, ForeignKey, DateTime, Date
import uuid
from sqlalchemy import Column,String
from sqlalchemy.orm import relationship

#todo test
# write a service function for when user period ends inside period_log for end_date
# add create new cycles inside of get period_log service when the period actually starts, create a new cycle

#todo
# include the new fields for the documentation_log table ans service tests
# connect everything together to retrieve the patterns before connecting  the llm

from database import Base
class CycleHistory(Base):
    __tablename__ = "cycle_history"
    __table_args__ = (
        UniqueConstraint("user_id", "start_date"),
    )

    id = Column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    period_log_id = Column(String, ForeignKey("period_log.id"), index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda :datetime.now(timezone.utc))
    document_logs = relationship("DocumentationLog", back_populates="cycle_history")
    user = relationship("User", back_populates="cycle_history")