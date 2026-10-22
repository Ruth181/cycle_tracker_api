from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Schemas.cycle_schema import CycleResponse
from Schemas.user_schema import UserResponseSchema, CreateUser, UpdateUser
from database import get_db_session
from Dependencies.auth_dependency import get_current_user
from Services.user_service import create_new_user, get_users, update_user, get_user,delete_user

user_router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@user_router.post("", status_code=201,response_model=UserResponseSchema)
def create_user(user:CreateUser, db:Session=Depends(get_db_session)):
    return create_new_user(user=user, db=db)

@user_router.get("", response_model=list[UserResponseSchema], status_code=200)
def _get_users(db:Session=Depends(get_db_session)):
    return get_users(db=db)

@user_router.patch("/me", status_code=200, response_model=UserResponseSchema)
def _update_user(payload:UpdateUser,current_user:User = Depends(get_current_user), db:Session=Depends(get_db_session)):
    return update_user(user_id=current_user.id, db=db, updated_payload=payload)

@user_router.get("/me", response_model=UserResponseSchema, status_code=200)
def _get_me(user:User = Depends(get_current_user)):
    return get_user(user)

@user_router.delete("/me", status_code=204)
def _delete_user(user:User = Depends(get_current_user), db:Session=Depends(get_db_session)):
    return delete_user(user=user,db=db)