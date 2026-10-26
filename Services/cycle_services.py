from email import message

from Models.Cycle import Cycle
from Schemas.cycle_schema import CreateCycle, UpdateCycle, Phases
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from utilities import (as_date,calculate_ovulation,
                       calculate_fertile_window,
                       calculate_next_period,
                       calculate_luteal,
                       calculate_follicular
                       )
from typing import List, Dict
#create cycle
def create_cycle(user_id: str, cycle:CreateCycle, db:Session):
    # convert string date to datetime object before adding to staging
    #normalized_date_str = datetime.strptime(cycle.first_day_last_period, "%d/%m/%Y").date()
    try:
        cycle_payload = Cycle(user_id=user_id,
                              first_day_last_period=cycle.first_day_last_period,
                              period_duration=int(cycle.period_duration),
                              cycle_length=int(cycle.cycle_length))
        db.add(cycle_payload)
        db.commit()
        db.refresh(cycle_payload)

        return cycle_payload

    except Exception as err:
        db.rollback()
        print(str(err))
        raise HTTPException(status_code=500, detail="Server Error")
    finally:
        db.close()


#update cycle
def update_cycle(user_id : str, cycle_id:str, updated_cycle : UpdateCycle, db:Session):
    try:
        existing_cycle = db.query(Cycle).filter(
            Cycle.user_id == user_id,
            Cycle.id == cycle_id
        ).first()

        if existing_cycle is None:
            raise HTTPException(status_code=404, detail="Cycle Not Found")

        if (existing_cycle.first_day_last_period is not None) and existing_cycle.first_day_last_period != updated_cycle.first_day_last_period:
            existing_cycle.first_day_last_period = updated_cycle.first_day_last_period

        if (existing_cycle.period_duration is not None) and existing_cycle.period_duration != updated_cycle.period_duration:
            existing_cycle.period_duration = updated_cycle.period_duration

        if (existing_cycle.cycle_length is not None) and existing_cycle.cycle_length != updated_cycle.cycle_length:
            existing_cycle.cycle_length = updated_cycle.cycle_length

        db.commit()
        db.refresh(existing_cycle)

        return existing_cycle

    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        print(str(err))
        raise HTTPException(status_code=500, detail="Server Error")


#get user cycle details
def get_cycle(user_id:str, db:Session):

    try:
        user_cycle = db.query(Cycle).filter(
            Cycle.user_id == user_id
        ).first()

        if user_cycle is None:
            raise HTTPException(status_code=404, detail="User cycle not found")

        return user_cycle

    except HTTPException:
        raise
    except Exception as e:
        print(f"Reason: {e}")
        raise HTTPException(status_code=500, detail="Server Error")
    finally:
        db.close()


def get_cycle_stats(db:Session, user_id:str):
    try:
        user_cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()

        if user_cycle is None:
            raise HTTPException(status_code=404, detail="User cycle not found")

        first_day_last_period = user_cycle.first_day_last_period
        cycle_length = user_cycle.cycle_length

        ovulation = calculate_ovulation(first_day_last_period,cycle_length)
        follicular_start = calculate_follicular(first_day_last_period,cycle_length)["start"]
        follicular_end = calculate_follicular(first_day_last_period,cycle_length)["end"]
        next_period = calculate_next_period(first_day_last_period,cycle_length)
        luteal_start = calculate_luteal(first_day_last_period,cycle_length)["start"]
        luteal_end = calculate_luteal(first_day_last_period,cycle_length)["end"]
        fertile_start = calculate_fertile_window(first_day_last_period,cycle_length)["start"]
        fertile_end = calculate_fertile_window(first_day_last_period,cycle_length)["end"]

        return {
            "next_period": next_period.date(),
            "ovulation" : ovulation.date(),
            "fertile_window" :{
                "start" : fertile_start.date(),
                "end" : fertile_end.date(),
            },
            "follicular": {
                "start" : follicular_start.date(),
                "end" : follicular_end.date(),
            },
            "luteal": {
                "start" : luteal_start.date(),
                "end" : luteal_end.date(),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Reason: ",str(e))
        raise HTTPException(status_code=500, detail="Server Error")

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
            "message" : message

        }

    except HTTPException:
        raise
    except Exception as e:
        print("Reason: ",str(e))
        raise HTTPException(status_code=500, detail="Server Error")


def predict_six_upcoming_cycles(db:Session, user_id:str):
    try:
        user_cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()

        if user_cycle is None:
            raise HTTPException(status_code=404, detail="User cycle not found")

        first_day_last_period = as_date(user_cycle.first_day_last_period)
        cycle_length = user_cycle.cycle_length
        period_duration = user_cycle.period_duration
        today = date.today()

        next_start = as_date(first_day_last_period)

        while next_start + timedelta(days=cycle_length) <= today:
            next_start += timedelta(days=cycle_length)


        if next_start < today and today > first_day_last_period + timedelta(days=period_duration):
            next_start += timedelta(days=cycle_length)

        cycles: List[Dict] = []
        current_start = next_start

        for i in range(1, 7):
            start_date = current_start
            end_date = start_date + timedelta(days=period_duration - 1)

            # Reuse your existing logic
            ovulation_date = as_date(calculate_ovulation(start_date, cycle_length))
            fertile = calculate_fertile_window(start_date, cycle_length)
            fertile_start = as_date(fertile["start"])
            fertile_end = as_date(fertile["end"])
            next_period_date = as_date(calculate_next_period(start_date, cycle_length))

            cycles.append({
                "cycle_number": i,
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "ovulation_date": ovulation_date,
                "fertile_window": {
                    "start": fertile_start,
                    "end": fertile_end
                },
                "next_period_preview": next_period_date
            })

            current_start = next_period_date

        return cycles
    except HTTPException:
        raise
    except Exception as e:
        print("Reason: ",str(e))
        raise HTTPException(status_code=500, detail="Server Error")



# def get_estimated_next_period_date(db:Session, user_id:str):
#     try:
#         cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()
#
#         if cycle is None:
#             raise HTTPException(status_code=404, detail="User cycle not found")
#
#         first_day_last_period = cycle.first_day_last_period
#         cycle_length = cycle.cycle_length
#
#         next_period = calculate_next_period(first_day_last_period,cycle_length)
#
#         return next_period.date()
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         print("Reason: ",str(e))
#         raise HTTPException(status_code=500, detail="Server Error")




