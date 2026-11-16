from fastapi import APIRouter, Depends
from sqlalchemy.engine import result

from Services.llm_service import generate_daily_message
from Services.documentation_log_services import get_recurring_patterns
from Dependencies.auth_dependency import get_current_user
from database import get_db_session
from Models.User import User
from sqlalchemy.orm import Session

llm_router = APIRouter(
    prefix="/llm",
    tags=["/LLM"],

)

@llm_router.get("/generate_daily_messages", status_code=200)
def get_daily_message(user:User = Depends(get_current_user), db:Session=Depends(get_db_session)):
    result : dict = get_recurring_patterns(user_id=user.id, db=db)
    return generate_daily_message(result)


