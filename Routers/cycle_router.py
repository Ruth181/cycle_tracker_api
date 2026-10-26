from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Dependencies.auth_dependency import get_current_user
from database import get_db_session
from Models.User import User
from Services.cycle_services import (create_cycle,
                                     update_cycle,
                                     get_cycle,
                                     get_cycle_stats,
                                     get_user_cycle_phase,
                                     predict_six_upcoming_cycles
                                     )
from Schemas.cycle_schema import (CycleResponse,
                                  CreateCycle,
                                  UpdateCycle,
                                  CycleStatResponse,
                                  CyclePhaseResponse,
                                  EstimatedCycleResponse)

cycle_router = APIRouter(
    prefix="/cycle",
    tags=["cycle"]
)

@cycle_router.post("", status_code=201, response_model=CycleResponse)
def _create_cycle(cycle:CreateCycle, user : User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return create_cycle(user_id=user.id, cycle=cycle, db=db)

@cycle_router.patch("/{cycle_id}", status_code=200, response_model=CycleResponse)
def _update_cycle(cycle_id:str, payload:UpdateCycle, user : User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return update_cycle(user_id=user.id, cycle_id=cycle_id, updated_cycle=payload, db=db)

@cycle_router.get("/my-cycle", response_model=CycleResponse, status_code=200)
def _get_user_cycle(user:User=Depends(get_current_user), db:Session=Depends(get_db_session)):
    return get_cycle(user_id=user.id, db=db)

@cycle_router.get("/stats", response_model=CycleStatResponse, status_code=200)
def _get_cycle_stats(user:User=Depends(get_current_user), db:Session=Depends(get_db_session)):
    return get_cycle_stats(user_id=user.id, db=db)

@cycle_router.get("/cycle-phase", response_model=CyclePhaseResponse, status_code=200)
def _get_cycle_phase(user:User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return  get_user_cycle_phase(user_id=user.id, db=db)

@cycle_router.get("/predict/6-months", response_model=list[EstimatedCycleResponse], status_code=200)
def predict_6_months(user :User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return predict_six_upcoming_cycles(user_id=user.id, db=db)


