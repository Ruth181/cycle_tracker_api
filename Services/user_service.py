from Models.User import User
from Schemas.cycle_schema import Phases
from Schemas.user_schema import CreateUser, UpdateUser
from sqlalchemy.orm import Session
from fastapi import HTTPException
from security import hash_password
from datetime import date, timedelta
from Models.Cycle import Cycle
from utilities import (calculate_ovulation,
                       calculate_fertile_window,
                       calculate_next_period,
                        get_day_of_cycle,

                       )

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
       user_exists = db.query(User).filter(User.id == user_id).first()

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

#calculate upcoming periods for 4 months
#google sign up
#instagram signup

#calculate the cycle phase 4 lutheal, menstral,follicular,ovulation
def get_user_cycle_phase(db:Session, user_id:str):
    today = date.today()

    try:
        user_cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()

        if user_cycle is None:
            raise HTTPException(status_code=404, detail="User cycle not found")

        first_day_last_period = user_cycle.first_day_last_period
        cycle_length = user_cycle.cycle_length
        period_duration = user_cycle.period_duration
        ovulation = calculate_ovulation(first_day_last_period,cycle_length)
        fertile_start = calculate_fertile_window(first_day_last_period,cycle_length)["start"]
        fertile_end = calculate_fertile_window(first_day_last_period,cycle_length)["end"]
        menstruation_end = first_day_last_period + timedelta(days=period_duration-1)
        next_period = calculate_next_period(first_day_last_period, cycle_length)


        if first_day_last_period.date() <= today <= menstruation_end.date():
            is_fertile = False
            phase = Phases.MENSTRATION
            message=""
        elif today == ovulation.date():
            is_fertile = True
            phase = Phases.OVULATION
            message = ""
        elif fertile_start.date() <= today <= fertile_end.date():
            is_fertile = True
            phase = Phases.FERTILE
            message = f"fertile from {fertile_start.date()} to {fertile_end.date()}"
        elif menstruation_end.date() < today < ovulation.date():
            is_fertile = False
            phase = Phases.FOLLICULAR
            message=""
        elif ovulation.date() < today < next_period.date():
            is_fertile = False
            phase = Phases.LUTEAL
            message=""

        else:
            phase = Phases.MENSTRATION
            is_fertile = False
            message=""

        return {
            "phase" : phase,
            "is_fertile" : is_fertile,
            "day" : get_day_of_cycle(cycle_start=user_cycle.first_day_last_period),
            "message" : message

        }

    except HTTPException:
        raise
    except Exception as e:
        print("Reason: ",str(e))
        raise HTTPException(status_code=500, detail="Server Error")
