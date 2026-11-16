from fastapi import HTTPException
#from sqlalchemy.exc import IntegrityError
import logging
#from datetime import date, timedelta
from sqlalchemy.orm import Session

from Models.CycleHistory import CycleHistory
# from exceptions import DuplicateCycleError, CycleError,CycleTooCloseError, CycleOutOfOrderError
# from utilities import _validate_basic, _update_average_cycle_length
from Services.period_log_services import create_period_log
from Schemas.Period_Log_schema import ConfirmPeriodRequest
from Schemas.cycle_history_schema import CreateNewCycle

logger = logging.getLogger(__name__)

# Gaps outside this range are accepted but excluded from the average,
# since they are more likely a missed entry than a real cycle length.
MIN_VALID_GAP = 15
MAX_VALID_GAP = 60
# Hard floor: two period starts closer than this are almost certainly a mistake.
MIN_ALLOWED_GAP = 10
RECENT_CYCLES_FOR_AVERAGE = 6
MIN_GAPS_FOR_AVERAGE = 2


#create a function, that creates a new log as well as create or start a new cycle but without an end date
def create_new_cycle_history(db:Session, user_id:str,
                             request:ConfirmPeriodRequest,
                             payload:CreateNewCycle,
                             commit:bool=False) -> CycleHistory:
    new_period_log = create_period_log(db,user_id,request, commit=False)

    new_cycle = CycleHistory(
        user_id=user_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        period_log_id=new_period_log.id
    )

    try:
        db.add(new_cycle)
        if commit:
            db.commit()
            db.refresh(new_cycle)
        else:
            db.flush()

        return new_cycle

    except HTTPException:
        if commit:
            db.rollback()
        raise
    except Exception as e:
        if commit:
            db.rollback()
        print("Reason : ", str(e))
        raise HTTPException(status_code=500, detail="Server Error")

#todo
# create cycle
# get cycles


def _get_latest_cycle(db: Session, user_id: str) -> type[CycleHistory] | None:
    cycle = db.query(CycleHistory).filter(CycleHistory.user_id == user_id).order_by(CycleHistory.start_date.desc()).first()
    return cycle

# def create_cycle(
#         db: Session,
#         user_id: str,
#         start_date: date,
#         period_end_date: date | None = None,
# ) -> CycleHistory:
#     """Record that a new period started on `start_date`.
#
#     Append-only: the new cycle must start after the user's latest one.
#     Closes the latest cycle and recomputes the average cycle length,
#     all in one transaction.
#     """
#     _validate_basic(start_date, period_end_date)
#
#     try:
#         latest = _get_latest_cycle(db, user_id)
#
#         if latest:
#             if start_date == latest.start_date:
#                 raise DuplicateCycleError("A cycle already starts on this date.")
#             if start_date < latest.start_date:
#                 raise CycleOutOfOrderError(
#                     "The start date must be after your latest cycle start."
#                 )
#             if (start_date - latest.start_date).days < MIN_ALLOWED_GAP:
#                 raise CycleTooCloseError(
#                     f"This is less than {MIN_ALLOWED_GAP} days after your previous cycle start."
#                 )
#             latest.end_date = start_date - timedelta(days=1)
#
#         new_cycle = CycleHistory(
#             user_id=user_id,
#             start_date=start_date,
#             period_log_id=period_end_date,
#             end_date=None,  # the newest cycle is always open
#         )
#         db.add(new_cycle)
#         db.flush()  # assigns new_cycle.id and surfaces unique-constraint errors
#
#         _update_average_cycle_length(db, user_id, RECENT_CYCLES_FOR_AVERAGE, MIN_VALID_GAP, MAX_VALID_GAP,MIN_GAPS_FOR_AVERAGE)
#
#         db.commit()
#         db.refresh(new_cycle)
#         return new_cycle
#
#     except IntegrityError:
#         # Two simultaneous requests creating the same cycle
#         db.rollback()
#         raise DuplicateCycleError("A cycle already starts on this date.")
#     except CycleError:
#         db.rollback()
#         raise
#     except Exception:
#         db.rollback()
#         logger.exception("Failed to create cycle for user %s", user_id)
#         raise

def get_all_cycles(db:Session, user_id:str):
    try:
        all_cycles = db.query(CycleHistory).filter(CycleHistory.user_id == user_id).order_by(CycleHistory.created_at.desc()).all()
        return all_cycles

    except Exception as e:
        print("Reason : ", str(e))
        raise HTTPException(status_code=400, detail="Server Error")


# def delete_latest_cycle(db: Session, user_id: str) -> Cycle:
#     """Undo the most recent cycle (e.g. an accidental 'Yes' tap).
#
#     - Deletes the latest cycle
#     - Reopens the previous cycle (end_date = None)
#     - Moves logs from the deleted cycle back onto the previous one
#     Returns the cycle that is now the latest.
#     """
#     try:
#         cycles = (
#             db.query(Cycle)
#             .filter(Cycle.user_id == user_id)
#             .order_by(Cycle.start_date.desc())
#             .limit(2)
#             .all()
#         )
#         if len(cycles) < 2:
#             # Deleting the only cycle would leave the user with no phase data
#             raise NothingToUndoError("There is no earlier cycle to go back to.")
#
#         latest, previous = cycles
#
#         logs = (
#             db.query(DocumentationLog)
#             .filter(
#                 DocumentationLog.user_id == user_id,
#                 DocumentationLog.cycle_id == latest.id,
#             )
#             .all()
#         )
#         for log in logs:
#             log.cycle_id = previous.id
#             # NOTE: uses `created_at` as the log date. If your log has its own
#             # `log_date` field, use that instead.
#             log.cycle_day = (log.created_at.date() - previous.start_date).days + 1
#
#         db.delete(latest)
#         previous.end_date = None
#
#         db.flush()
#         _update_average_cycle_length(db, user_id)
#
#         db.commit()
#         db.refresh(previous)
#         return previous
#
#     except CycleError:
#         db.rollback()
#         raise
#     except Exception:
#         db.rollback()
#         logger.exception("Failed to undo latest cycle for user %s", user_id)
#         raise
