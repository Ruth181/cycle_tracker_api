from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Schemas.auth_schema import AuthLogin, AuthResponse
from Services.auth_service import login_service
from database import get_db_session


auth_router = APIRouter(prefix="/auth", tags=["Auth"])

#login endpiont
@auth_router.post("/login", response_model=AuthResponse, status_code=200)
def login(user:AuthLogin, db:Session = Depends(get_db_session)):
    return login_service(details=user, db=db)


# {
#   "email": "ruthG@example.com",
#   "password": "GeorgeRuth_19"
# }

  # "email": "mina@example.com",
  # "password": "MinaDermitas@18"