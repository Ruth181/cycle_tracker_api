from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db_session
from Dependencies.auth_dependency import get_current_user
from Models.User import User
from Services.period_log_services import get_cycle_status, confirm_period_ends, get_all_period_logs, create_period_log
from Schemas.Period_Log_schema import GetCyclePhaseResponse, GetPeriodLogResponse, ConfirmPeriodEndedRequest, \
    ConfirmPeriodRequest

period_log_router = APIRouter(
    prefix="/period_log",
    tags=["Period Log"]
)

@period_log_router.get("", status_code=200, response_model=list[GetPeriodLogResponse])
def get_period_logs(user : User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return get_all_period_logs(db=db, user_id=user.id)

@period_log_router.get("/cycle_status", status_code=200, response_model=GetCyclePhaseResponse)
def cycle_status(user:User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return get_cycle_status(db=db, user_id=user.id)

@period_log_router.post("", status_code=201, response_model=GetPeriodLogResponse)
def create_new_period_log(req:ConfirmPeriodRequest, user:User = Depends(get_current_user),db:Session = Depends(get_db_session)):
    return create_period_log(req=req, user_id=user.id, db=db)

@period_log_router.post("/period_ended", status_code=200, response_model=GetPeriodLogResponse)
def set_period_ended(payload : ConfirmPeriodEndedRequest,user:User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return confirm_period_ends(db=db, user_id=user.id, req=payload)
