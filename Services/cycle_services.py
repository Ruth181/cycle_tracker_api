from Models.Cycle import Cycle
from Schemas.Period_Log_schema import ConfirmPeriodRequest
from Schemas.cycle_schema import CreateCycle, UpdateCycle, Phases
from Schemas.cycle_history_schema import CreateNewCycle
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from Services.user_service import get_user_cycle_phase
from utilities import (as_date,calculate_ovulation,
                       calculate_fertile_window,
                       calculate_next_period,
                       calculate_luteal,
                       calculate_follicular
                       )
from typing import List, Dict
from Services.cycle_history_service import create_new_cycle_history
from Models.Period_Log import PeriodLog
from Models.CycleHistory import CycleHistory
from Services.period_log_services import create_period_log

#create cycle
def create_cycle(user_id: str, cycle:CreateCycle, db:Session):

    req = ConfirmPeriodRequest(came = True,actual_start_date=cycle.first_day_last_period,estimated_end_date=cycle.estimated_end_date)
    cycles_payload = CreateNewCycle(start_date=cycle.first_day_last_period)

    cycle_payload = Cycle(user_id=user_id,
                  first_day_last_period=cycle.first_day_last_period,
                  period_duration=int(cycle.period_duration),
                  cycle_length=int(cycle.cycle_length))
    db.add(cycle_payload)
    try:
        create_new_cycle_history(db=db, user_id=user_id, request=req, payload=cycles_payload, commit=False)
        db.commit()
        db.refresh(cycle_payload)

        return cycle_payload
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        print(str(err))
        raise HTTPException(status_code=500, detail="Server Error")

#update cycle
def update_cycle(user_id : str, updated_cycle : UpdateCycle, db:Session):
    try:
        existing_cycle = db.query(Cycle).filter(
            Cycle.user_id == user_id
        ).first()

        if existing_cycle is None:
            raise HTTPException(status_code=404, detail="Cycle Not Found")

        if (updated_cycle.first_day_last_period is not None) and existing_cycle.first_day_last_period != updated_cycle.first_day_last_period:
            existing_cycle.first_day_last_period = updated_cycle.first_day_last_period

        if (updated_cycle.period_duration is not None) and existing_cycle.period_duration != updated_cycle.period_duration:
            existing_cycle.period_duration = updated_cycle.period_duration

        if (updated_cycle.cycle_length is not None) and existing_cycle.cycle_length != updated_cycle.cycle_length:
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


def confirm_end_of_cycle(db:Session, user_id:str, req:ConfirmPeriodRequest):
    try:
        cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()

        if cycle is None:
            raise HTTPException(status_code=404,detail="Cycle not found")

        # get the period log, the one with the user id and date corresponding to payload, to retrieve the ID
        previous_period_log = (db.query(PeriodLog).filter(
            PeriodLog.user_id == user_id,
            PeriodLog.start_date < req.actual_start_date
        ).order_by(
            PeriodLog.start_date.desc()
        ).first())

        if previous_period_log is None:
            raise HTTPException(status_code=404,detail="Period Log not found")

        #use the period log id to retrieve the user cycle using the user_id, period_log_id and the end_Date is None
        get_specific_cycle = db.query(CycleHistory).filter(CycleHistory.user_id == user_id,
                             CycleHistory.period_log_id == previous_period_log.id,
                             CycleHistory.end_date.is_(None)).first()

        if get_specific_cycle is None:
            raise HTTPException(status_code=404,detail="Cycle not found")

        if req.came:
            # replace None with the actual end_date if the cycle. A day before the new cycle begins
            get_specific_cycle.end_date = req.actual_start_date - timedelta(days=1)

            new_log = create_period_log(db,user_id,req)

            #reset cycle.first_day_last_period to when the period actually starts
            cycle.first_day_last_period = req.actual_start_date

            # create a new cycle inside cycleHistory, with end_Date None, which will be updated with the new cycle begins and the old cycle ends
            new_cycle = CycleHistory(
                user_id=user_id,
                start_date=req.actual_start_date,
                end_date= None,
                period_log_id = new_log.id
            )
            db.add(new_cycle)
            db.commit()
            db.refresh(new_cycle)

            return {
                "message" : "Period Confirmed and Updated",
                "next_period" : calculate_next_period(req.actual_start_date, cycle.cycle_length),
            }
        else:
            return {
                "message" : "Got it!, we'll check again tomorrow",
                "state" : get_user_cycle_phase(db=db, user_id=user_id)["phase"]
            }

    except HTTPException:
        raise

    except Exception as ex:
        print("Reason: ",str(ex))
        raise HTTPException(status_code=500,detail="Server Error")


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




