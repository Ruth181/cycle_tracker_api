from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Models.User import User
from Dependencies.auth_dependency import get_current_user
from Schemas.documentation_log_schema import ReqDocumentationLog,ResponseDocumentationLog
from database import get_db_session
from Services.documentation_log_services import get_history,get_log_by_id,add_new_log

documentation_router = APIRouter(
    prefix="/doc_logs",
    tags=["Documentation Log"]
)

@documentation_router.get("", response_model=list[ResponseDocumentationLog],status_code=200)
def get_all_logs_by_user(user:User = Depends(get_current_user), db:Session=Depends(get_db_session)):
    return get_history(db=db, user_id=user.id)

@documentation_router.get("/{log_id}", response_model=ResponseDocumentationLog, status_code=200)
def get_one_log(log_id:str, user:User = Depends(get_current_user), db:Session=Depends(get_db_session)):
    return get_log_by_id(db=db, log_id=log_id, user_id=user.id)

@documentation_router.post("", response_model=ResponseDocumentationLog,status_code=201)
def create_log(log:ReqDocumentationLog, user:User = Depends(get_current_user), db:Session=Depends(get_db_session)):
    return add_new_log(log=log, user_id=user.id, db=db)
