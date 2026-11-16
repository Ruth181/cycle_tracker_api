from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from Models.Cycle import Cycle
from Schemas.cycle_schema import Phases
from utilities import calculate_next_period, as_date
from Schemas.Period_Log_schema import ConfirmPeriodRequest, ConfirmPeriodEndedRequest,GetPeriodLogResponse
from Models.Period_Log import PeriodLog
from Models.CycleHistory import CycleHistory
from Services.user_service import get_user_cycle_phase


def get_all_period_logs(db:Session, user_id:str) -> List[GetPeriodLogResponse]:
    try:
        return db.query(PeriodLog).filter(PeriodLog.user_id == user_id).all()
    except Exception as ex:
        print("Reason: ",str(ex))
        raise HTTPException(status_code=500,detail="Server Error")

def get_cycle_status(db:Session, user_id:str):
    try:
        cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()
        if cycle is None:
            raise HTTPException(status_code=404,detail="Cycle not found")

        first_day = as_date(cycle.first_day_last_period)
        next_period = as_date(calculate_next_period(first_day,cycle.cycle_length))
        today = date.today()

        days_late = (today - next_period).days

        if today < next_period:
            return {
                "state": "Normal",
                "next_period": next_period,
                "phase" : get_user_cycle_phase(db=db, user_id=user_id)["phase"]
            }
        elif 0 <= days_late <= 7:
            return {
                "state" : "Needs Confirmation",
                "next_period": next_period,
                "days_late": days_late,
                "message" : f"Your period was expected on {next_period}. Did it start? Yes/No",
                "phase" : Phases.LUTEAL
            }
        else:
            return {
                "state" : "Late",
                "days_late": days_late,
                "next_period": next_period
            }

    except HTTPException:
        raise

    except Exception as ex:
        print("Reason: ",str(ex))
        raise HTTPException(status_code=500,detail="Server Error")


def create_period_log(db:Session, user_id:str, req:ConfirmPeriodRequest, commit=True):
    try:
        find_log = db.query(PeriodLog).filter(
            PeriodLog.user_id == user_id,
            PeriodLog.start_date == req.actual_start_date
        ).order_by(
            PeriodLog.start_date.desc()
        ).first()

        if find_log is not None:
            raise HTTPException(status_code=409,detail="Period Log already exists")

        new_log = PeriodLog(
            user_id=user_id,
            start_date=req.actual_start_date,
            estimated_end_date=req.estimated_end_date,
        )

        db.add(new_log)

        if commit:
            db.commit()
            db.refresh(new_log)
        else:
            db.flush()

        return new_log

    except HTTPException:
        if commit:
            db.rollback()
        raise

    except Exception as ex:
        if commit:
            db.rollback()
        print("Reason: ",str(ex))
        raise HTTPException(status_code=500,detail="Server Error")


def confirm_period_ends(db:Session, user_id:str,req:ConfirmPeriodEndedRequest):
    try:
        period_log = db.query(PeriodLog).filter(
            PeriodLog.user_id == user_id,
            PeriodLog.start_date == req.actual_start_date,
            PeriodLog.estimated_end_date.is_(None)
        ).order_by(
            PeriodLog.start_date.desc()
        ).first()

        if period_log is None:
            raise HTTPException(status_code=404,detail="Period Log not found")

        if req.ended:
            period_log.estimated_end_date = req.estimated_end_date
            db.commit()

        return period_log

    except HTTPException:
        raise

    except Exception as ex:
        print("Reason: ",str(ex))
        raise HTTPException(status_code=500,detail="Server Error")


# def confirm_period(db:Session, user_id:str, req:ConfirmPeriodRequest):
#     try:
#         cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()
#
#         if cycle is None:
#             raise HTTPException(status_code=404,detail="Cycle not found")
#
#         if req.came:
#             new_log = PeriodLog(
#                 user_id = user_id,
#                 start_date=req.actual_start_date
#             )
#
#             db.add(new_log)
#             #reset cycle.first_day_last_period to when the period actually starts
#             cycle.first_day_last_period = req.actual_start_date
#             db.commit()
#             db.refresh(new_log)
#
#             return {
#                 "message" : "Period Confirmed and Updated",
#                 "next_period" : calculate_next_period(req.actual_start_date, cycle.cycle_length),
#             }
#         else:
#             return {
#                 "message" : "Got it!, we'll check again tomorrow",
#                 "state" : Phases.LUTEAL
#             }
#
#     except HTTPException:
#         raise
#
#     except Exception as ex:
#         print("Reason: ",str(ex))
#         raise HTTPException(status_code=500,detail="Server Error")