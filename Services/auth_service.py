from Schemas.auth_schema import AuthLogin, ReqGoogleLoginIn
from sqlalchemy.orm import Session
from Models.User import User
from fastapi import HTTPException
from security import verify_password, create_access_token, verify_google_token
from sqlalchemy.exc import IntegrityError
from Schemas.auth_schema import AuthResponse
from security import create_access_token

def login_service(details:AuthLogin, db:Session):
    try:
        user = db.query(User).filter(User.email == details.email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        if not verify_password(details.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid Credentials")

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


def google_auth(body : ReqGoogleLoginIn, db:Session):

    claims = verify_google_token(body.id_token)

    if not claims.get("email_verified"):
        raise HTTPException(status_code=400, detail="Email Verification Failed")

    sub = claims["sub"]
    email = claims["email"].strip().lower()

    user = db.query(User).filter(User.google_sub == sub).first()

    if user is None:
        #link an existing account with the same email to the google sign in
        user = db.query(User).filter(User.email == email).first()
        if user is not None:
            user.google_sub = sub
            db.commit()

    if user is None:
        user = User(
            full_name= claims.get("name"),
            email= email,
            google_sub = sub
        )
        db.add(user)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=500, detail="Could not create or find user")

    return AuthResponse(
        access_token=create_access_token(str(user.id)),
        token_type="bearer"
    )
