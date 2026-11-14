import uuid
from uuid import UUID

from pydantic import BaseModel, field_validator
from datetime import date, datetime, timedelta
from Schemas.cycle_schema import Phases
from Schemas.cycle_schema import CyclePhaseResponse

class ConfirmPeriodRequest(BaseModel):
    came : bool
    actual_start_date : datetime = date.today()
    estimated_end_date : datetime | None = None

    @field_validator('actual_start_date', mode="before")
    @classmethod
    def normalize_first_day_period_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v

    @field_validator('estimated_end_date', mode="before")
    @classmethod
    def normalize_end_day_last_period(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v

class ConfirmPeriodEndedRequest(BaseModel):
    ended : bool
    actual_start_date : datetime
    estimated_end_date : datetime = date.today()

    @field_validator('actual_start_date', mode="before")
    @classmethod
    def normalize_actual_first_day_period_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v

    @field_validator('estimated_end_date', mode="before")
    @classmethod
    def normalize_last_day_period_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v

class ConfirmPeriodResponse(BaseModel):
    message: str
    next_period : date | None = None
    state : str | None = None

class GetCyclePhaseResponse(BaseModel):
    state: str
    next_period: date
    days_late : int | None = None
    message: str | None = None
    phase : CyclePhaseResponse | Phases | None = None


class GetPeriodLogResponse(BaseModel):
    id : UUID
    user_id :str
    start_date : datetime
    estimated_end_date : datetime | None = None
    created_at : datetime