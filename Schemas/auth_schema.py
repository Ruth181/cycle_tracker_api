from pydantic import BaseModel, Field, EmailStr,field_validator
import string

class AuthLogin(BaseModel):
    email : EmailStr
    password : str = Field(min_length=8, max_length=20)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value):
        return value.lower().strip()

    @field_validator('password')
    @classmethod
    def check_password(cls, value : str):
        if not any(character.isdigit() for character in value):
            raise ValueError('Password must contain at least 1 digit')
        elif not any(character.isupper() for character in value):
            raise ValueError('Password must contain at least 1 uppercase letter')
        elif not any(character in string.punctuation for character in value):
            raise ValueError('Password must contain at least 1 Special Character')

        return value

class AuthResponse(BaseModel):
    access_token : str
    token_type:str
