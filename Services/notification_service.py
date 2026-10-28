from datetime import date, timedelta
from fastapi import HTTPException

from sqlalchemy.orm import Session
from utilities import calculate_next_period,as_date
from Models.Cycle import Cycle


def get_notification(user_id:int, db:Session):
    try:
        cycle = db.query(Cycle).filter(Cycle.user_id == user_id).first()

        if cycle is None:
            raise HTTPException(status_code=404, detail="Cycle not found")


        first_day_last_period = cycle.first_day_last_period
        cycle_length = cycle.cycle_length

        next_period = as_date(calculate_next_period(first_day_last_period, cycle_length))
        today = date.today()

        while next_period < today:
            next_period += timedelta(days=cycle.cycle_length)

            days_to_period = (next_period - today).days

            if days_to_period > 7:
                return {
                    "notify":False,
                    "message" : f"Your next period is in {days_to_period} days.",
                }
            if days_to_period > 1:
                return {
                    "notify": True,
                    "message" : f"Your next period is in {days_to_period} days.",
                }
            if days_to_period == 1:
                return {
                    "notify": True,
                    "message" : "1 day to your Period"
                }
            if days_to_period == 0:
                return {
                    "notify": True,
                    "message" : "Your Period is today."
                }

            return {
                "notify": False,
                "message" : ""
            }

    except HTTPException:
        raise

    except Exception as err:
        print("Reason: ", str(err))
        raise HTTPException(status_code=500, detail="Server Error")