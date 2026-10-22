from Models.User import User
from Schemas.user_schema import CreateUser, UpdateUser
from sqlalchemy.orm import Session
from fastapi import HTTPException
from security import hash_password


def get_users(db:Session):
    try:
        users = db.query(User).all()
        return users

    except HTTPException:
        raise HTTPException(status_code=500, detail="Server Error")


#create_user
def create_new_user(db:Session, user:CreateUser):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user is not None:
            raise HTTPException(status_code=409, detail="user already exists")

        new_user = User(
            full_name = user.full_name,
            email = user.email,
            age = user.age,
            gender = user.gender,
            password_hash = hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Reason: {e}")
        raise HTTPException(status_code=500, detail="Server Error")


#update user
def update_user(user_id:str, updated_payload:UpdateUser, db:Session):
    try:
        existing_user = db.query(User).filter(User.id == user_id).first()

        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if (updated_payload.full_name is not None) and updated_payload.full_name != existing_user.full_name:
            existing_user.full_name = updated_payload.full_name

        if(updated_payload.age is not None) and existing_user.age != updated_payload.age:
            existing_user.age = updated_payload.age

        if (updated_payload.gender is not None) and existing_user.gender.lower() != updated_payload.gender.lower():
            existing_user.gender = updated_payload.gender

        db.commit()
        db.refresh(existing_user)
        return existing_user

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Reason: {e}")
        raise HTTPException(status_code=500, detail="Server Error")

    finally:
        db.close()

#get user
def get_user(user : User):
    return user



#delete_account
def delete_user(user_id:str, db:Session):
    try:
       user_exists = db.query(User).filter(User.id == user_id)

       if user_exists is None:
           raise HTTPException(status_code=404, detail="User not found")

       db.delete(user_exists)
       db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Reason: {e}")
        raise HTTPException(status_code=500, detail="Server Error")

    finally:
        db.close()

#calculate upcoming periods for 4 months
#google sign up
#instagram signup
