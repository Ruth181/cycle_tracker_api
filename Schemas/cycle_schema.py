from pydantic import BaseModel,Field, field_validator
from uuid import UUID
from datetime import datetime, date
from enum import Enum

class Phases(str, Enum):
    FOLLICULAR = "FOllicular"
    LUTEAL = "Luteal"
    OVULATION = "Ovulation"
    FERTILE = "Fertile"
    MENSTRATION = "Menstration"

class CreateCycle(BaseModel):
    first_day_last_period : datetime = Field(description="First day of last period")
    period_duration : int = Field(ge=1, description="Period Duration")
    cycle_length : int = Field(description="Cycle Length", gt=10)

    @field_validator('first_day_last_period', mode="before")
    @classmethod
    def normalize_first_day_last_period_date(cls, v):
        if isinstance(v,str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v


class UpdateCycle(BaseModel):
    first_day_last_period : datetime | None = None
    period_duration : int | None = None
    cycle_length : int | None = None

    @field_validator('first_day_last_period', mode="before")
    @classmethod
    def normalize_first_day_last_period_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y")
        return v


class CycleResponse(BaseModel):
    id : UUID
    user_id : UUID
    first_day_last_period : datetime
    period_duration : int
    cycle_length : int
    created_at : datetime


class PhaseWindow(BaseModel):
    start : date
    end : date

class CycleStatResponse(BaseModel):
    next_period : date
    ovulation : date
    fertile_window : PhaseWindow
    follicular : PhaseWindow
    luteal : PhaseWindow

class CyclePhaseResponse(BaseModel):
    phase : Phases
    is_fertile : bool
    message : str | None = None


class EstimatedCycleResponse(BaseModel):
    cycle_number : int
    period : PhaseWindow
    ovulation_date : date
    fertile_window : PhaseWindow
    next_period_preview : date