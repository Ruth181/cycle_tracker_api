from fastapi import APIRouter, Depends

from Services.notification_service import get_notification
from sqlalchemy.orm import Session
from Models.User import User
from database import get_db_session
from Dependencies.auth_dependency import get_current_user
from Schemas.notification_schema import NotificationResponse

notification_router = APIRouter(
    prefix="/notification",
    tags=["Notification"]
)

@notification_router.get("", response_model=NotificationResponse, status_code=200)
def _get_notification(user : User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    return get_notification(db=db, user_id=user.id)
