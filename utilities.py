from datetime import datetime, timedelta, date
from exceptions import CycleError, CycleTooCloseError,FutureStartDateError
from Models.CycleHistory import CycleHistory as Cycle
from Models.Documentation_Log import DocumentationLog
from sqlalchemy.orm import Session

def calculate_period_days_remaining(period_duration:int, last_period_first_day : datetime):
    return last_period_first_day + timedelta(days=period_duration -1)

def calculate_next_period(last_period_first_day : datetime, cycle_length : int):
    return last_period_first_day + timedelta(days=cycle_length)

def calculate_ovulation(last_period_first_day : datetime, cycle_length : int):
    return  last_period_first_day + timedelta(days=cycle_length -14)

def calculate_follicular(last_period_first_day : datetime, cycle_length : int) -> dict:
    follicular_end = calculate_ovulation(last_period_first_day, cycle_length) - timedelta(days=1)
    return {
        "start" : last_period_first_day,
        "end" :  follicular_end
    }

def calculate_luteal(last_period_first_day : datetime, cycle_length : int) -> dict:
    luteal_start = calculate_ovulation(last_period_first_day, cycle_length) + timedelta(days=1)
    luteal_end = calculate_next_period(last_period_first_day,cycle_length) - timedelta(days=1)

    return {
        "start" : luteal_start,
        "end" : luteal_end
    }


def calculate_fertile_window(last_period_first_day : datetime, cycle_length : int) -> dict:
    ovulation = calculate_ovulation(last_period_first_day, cycle_length)
    return {
        "start" : (ovulation - timedelta(days=5)),
        "end" : (ovulation + timedelta(days=1))
    }

def as_date(d):
    return d.date() if isinstance(d, datetime) else d

def calculate_date(start_date:date, end_date:date) -> bool:
    today_date = date.today()
    start = date(start_date.year, start_date.month,start_date.day)
    end = date(end_date.year, end_date.month, end_date.day)

    if start <= today_date <= end:
        return True

    return False

def get_day_of_cycle(cycle_start : datetime, target_date : date = date.today()) -> int | None:
    if cycle_start is None:
        return None
    cycle_start_date = as_date(cycle_start)
    day = (target_date - cycle_start_date).days + 1

    if day < 1:
        return None

    return day

def _validate_basic(start_date: date, period_end_date: date | None) -> None:
    if start_date > date.today():
        raise FutureStartDateError("Cycle start date cannot be in the future.")
    if period_end_date and period_end_date < start_date:
        raise CycleError("Period end date cannot be before the start date.")


def _validate_gaps(start_date: date, previous: Cycle | None, following: Cycle | None, min_allowed_gap : int) -> None:
    if previous and (start_date - previous.start_date).days < min_allowed_gap:
        raise CycleTooCloseError(
            f"This is less than {min_allowed_gap} days after your previous cycle start."
        )
    if following and (following.start_date - start_date).days < min_allowed_gap:
        raise CycleTooCloseError(
            f"This is less than {min_allowed_gap} days before your next cycle start."
        )



def _update_average_cycle_length(db: Session, user_id: str,
               recent_cycles_for_average : int,
               min_valid_gap : int,
               max_valid_gap : int,
               min_gaps_for_average : int
) -> None:
    rows = (
        db.query(Cycle.start_date)
        .filter(Cycle.user_id == user_id)
        .order_by(Cycle.start_date.desc())
        .limit(recent_cycles_for_average + 1)
        .all()
    )
    starts = sorted(r[0] for r in rows)
    gaps = [(b - a).days for a, b in zip(starts, starts[1:])]
    valid = [g for g in gaps if min_valid_gap <= g <= max_valid_gap]

    settings = db.query(Cycle).filter(Cycle.user_id == user_id).first()
    if not settings:
        return

    if len(valid) >= min_gaps_for_average:
        settings.average_cycle_length = round(sum(valid) / len(valid))
    # Otherwise leave it as is; phase calculation falls back to
    # settings.typical_cycle_length until there is enough history.


if __name__ == "__main__":
    first_period_first_day = datetime.strptime("29/09/2026", "%d/%m/%Y")
    print(calculate_next_period(first_period_first_day, 22))
    print(calculate_fertile_window(first_period_first_day,22))
