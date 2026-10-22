from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr
import string
import enum
from uuid import UUID

class Gender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"


class CreateUser(BaseModel):
    full_name : str = Field(description="Full name of the user", min_length=5)
    age : int = Field(description="Age of the user", ge=9)
    gender : Gender = Field(default=Gender.FEMALE)
    email : EmailStr
    password : str = Field(description="Password of the user", min_length=8, max_length=20)

    @field_validator('full_name')
    @classmethod
    def full_name_validator(cls, v:str):
        if any(char.isdigit() for char in v):
            raise ValueError("Name must not contain digits")

        if any(char in string.punctuation  for char in v):
            raise ValueError("Name must not contain any special characters")

        return v.strip()

    @field_validator('email')
    @classmethod
    def email_validator(cls, v:str):
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def password_validator(cls, v:str):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must not contain at least 1 digit")

        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least 1 uppercase letter")

        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least 1 lowercase letter")

        if not any(char in string.punctuation for char in v):
            raise ValueError("Password must contain at least 1 special character")

        return v

class UpdateUser(BaseModel):
    full_name : str | None = None
    age : int | None= None
    gender : Gender | None = None
    #email : EmailStr | None = None


class UserResponseSchema(BaseModel):
    id : UUID
    full_name : str
    email : EmailStr
    age : int
    role : str
    gender : Gender
    created_at : datetime