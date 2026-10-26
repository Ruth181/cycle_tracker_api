from datetime import datetime

from pydantic import BaseModel, Field
from enum import Enum

class Intensity(str,Enum):
    NONE = "None"
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"

class ReqDocumentationLog(BaseModel):
    is_period : bool = Field(description="Whether the log is during your period or not", default=False)
    flow_intensity :Intensity | None = None
    symptoms : list[str] = Field(description="A list of symptoms associated with this log")
    other_symptoms : str | None = Field(description="A list of other symptoms associated with this log", default=None)


class ResponseDocumentationLog(BaseModel):
    id : str
    user_id : str
    is_period : bool
    flow_intensity : Intensity | None
    symptoms : list[str]
    other_symptoms : str | None
    created_at : datetime

