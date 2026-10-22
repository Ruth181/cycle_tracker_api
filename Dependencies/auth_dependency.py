from fastapi import Depends
from sqlalchemy.orm import Session

from security import decode_access_token
from jose import JWTError, ExpiredSignatureError
from fastapi import HTTPException
from Models.User import User
from database import get_db_session
from fastapi.security import OAuth2PasswordBearer

oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(access_token :str=Depends(oauth_bearer) , db_session:Session=Depends(get_db_session)):
    # decode token & #catch the exceptions
    try:
        decoded_token = decode_access_token(access_token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired Token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

    # extract the user_id from sub
    user_id = decoded_token["sub"]

    user = db_session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized User")

    # return user
    return user


