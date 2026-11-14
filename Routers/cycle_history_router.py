from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from Models.User import User
from Dependencies.auth_dependency import get_current_user
from database import get_db_session
from Services.cycle_history_service import  get_all_cycles
from Schemas.cycle_history_schema import CyclesResponse
#from exceptions import  DuplicateCycleError,FutureStartDateError,CycleOutOfOrderError,CycleTooCloseError,CycleError


cycle_history_router = APIRouter(
    prefix="/cycle-history",
    tags=["cycle-history"]
)

@cycle_history_router.get("", status_code=200, response_model=list[CyclesResponse])
def get_cycles(user:User = Depends(get_current_user), db:Session = Depends(get_db_session)):
    return get_all_cycles(db=db, user_id=user.id)


# @cycle_history_router.post("/cycles", status_code=201)
# def add_cycle(
#     payload: CreateNewCycle,
#     db: Session = Depends(get_db_session),
#     current_user = Depends(get_current_user),
# ):
#     try:
#         return create_cycle(db, current_user.id, payload.start_date, payload.period_end_date)
#     except DuplicateCycleError as e:
#         raise HTTPException(status_code=409, detail=str(e))
#     except (FutureStartDateError, CycleOutOfOrderError, CycleTooCloseError) as e:
#         raise HTTPException(status_code=422, detail=str(e))
#     except CycleError as e:
#         raise HTTPException(status_code=400, detail=str(e))