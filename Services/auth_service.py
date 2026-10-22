from Schemas.auth_schema import AuthLogin
from sqlalchemy.orm import Session
from Models.User import User
from fastapi import HTTPException
from security import verify_password, create_access_token

def login_service(details:AuthLogin, db:Session):
    try:
        user = db.query(User).filter(User.email == details.email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        if not verify_password(details.password, user.password_hash):
            raise HTTPException(status_code=404, detail="Invalid Credentials")

        access_token = create_access_token(user.id)

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise

    except Exception as ex:
        print(f"Something went wrong {str(ex)}")
        raise HTTPException(status_code=500, detail="Server Error")
