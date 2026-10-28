from pydantic import BaseModel

class NotificationResponse(BaseModel):
    notify : bool
    message: str | None = None

