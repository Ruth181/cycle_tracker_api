import bcrypt
from config import settings
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt

JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES = 30

def hash_password(password:str) -> str :
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(user_id:str) -> str:
    #formular for expiry the current time + 30 minutes
    expire =  datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES)

    #create the payload for the user identity inside the token
    payload = {
        "sub" : user_id,
        "exp" : expire
    }
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(access_token:str):
    decoded_user = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    if 'sub' not in decoded_user:
        raise JWTError()

    return decoded_user


if __name__ == "__main__":
    from datetime import datetime
    print(datetime.strptime("29/10/2026", "%d/%m/%Y"))
    #print(decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxYjQyZjYxOS05NDIzLTQzNTYtODIzYS0zYzBhODFlNDQzNzMiLCJleHAiOjE3OTI1MDMyODF9.Pw4kEG_HN6AWgfso1YXbvnPtNChv3orsiMgDIMWae_s"))