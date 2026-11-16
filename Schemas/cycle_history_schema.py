from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

class CreateNewCycle(BaseModel):
    start_date: datetime
    end_date: datetime | None = None
    period_log_id: UUID | None = None

    @field_validator('start_date', mode="before")
    @classmethod
    def normalize_actual_first_day_period_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v

    @field_validator('end_date', mode="before")
    @classmethod
    def normalize_last_day_period_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v


class CyclesResponse(BaseModel):
    id : UUID | None = None
    user_id : UUID | None = None
    start_date : datetime | None = None
    end_date : datetime | None = None
    period_log_id : UUID | None = None
    created_at : datetime | None = None