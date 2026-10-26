from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db_session
from Dependencies.auth_dependency import get_current_user
from Models.User import User
from Services.period_log_services import confirm_period, get_cycle_status
from Schemas.Period_Log_schema import ConfirmPeriodRequest, ConfirmPeriodResponse, GetCyclePhaseResponse

period_log_router = APIRouter(
    prefix="/period_log",
    tags=["Period Log"]
)

@period_log_router.get("/cycle_status", status_code=200, response_model=GetCyclePhaseResponse)
def cycle_status(user:User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return get_cycle_status(db=db, user_id=user.id)

@period_log_router.post("", status_code=201, response_model=ConfirmPeriodResponse)
def create_confirm_period(payload : ConfirmPeriodRequest, user:User = Depends(get_current_user),db:Session = Depends(get_db_session)):
    return confirm_period(db=db, user_id=user.id, req=payload)