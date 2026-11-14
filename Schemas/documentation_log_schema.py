from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from enum import Enum
from Schemas.cycle_schema import Phases

class Intensity(str,Enum):
    NONE = "None"
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"

class ReqDocumentationLog(BaseModel):
    is_period : bool = Field(description="Whether the log is during your period or not", default=False)
    #phase : Phases = Field(description="The cycle phase of the log")
    moods : list[str] = Field(description="The mood of the log")
    flow_intensity :Intensity | None = None
    symptoms : list[str] = Field(description="A list of symptoms associated with this log")
    other_symptoms : str | None = Field(description="A list of other symptoms associated with this log", default=None)

# class RecurringSymptomsResponse(BaseModel):
#     phase: Any,
#     day: int,
#     recurring_symptoms : list[dict],
#     recurring_moods : list[dict],
#     recent_symptoms : Any,
#     recent_moods : Any,
#     confidence : str

class ResponseDocumentationLog(BaseModel):
    id : str
    user_id : str
    is_period : bool
    moods : list[str]
    phase : Phases
    flow_intensity : Intensity | None
    symptoms : list[str]
    other_symptoms : str | None
    created_at : datetime

