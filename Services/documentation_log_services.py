from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Documentation_Log import DocumentationLog
from Schemas.documentation_log_schema import ReqDocumentationLog
from Services.user_service import get_user_cycle_phase
import logging
from collections import Counter, defaultdict
from Models.Cycle import Cycle
from Models.CycleHistory import CycleHistory

# get notifications
# get symptoms
# create logs and get history
def add_new_log(log:ReqDocumentationLog, user_id:str, db:Session):
    cycle = db.query(Cycle).filter(
        Cycle.user_id == user_id
    ).first()
    if cycle is None:
        raise HTTPException(status_code=404, detail="Cycle not found")
    cycle_history = db.query(CycleHistory).filter(CycleHistory.user_id == user_id,
                                                  CycleHistory.start_date == cycle.first_day_last_period,
                                                  CycleHistory.end_date.is_(None)).first()
    if cycle_history is None:
        raise HTTPException(status_code=404, detail="Cycle History not found")
    try:
        new_log = DocumentationLog(
            is_period = log.is_period,
            flow_intensity = log.flow_intensity,
            moods = log.moods,
            symptoms = log.symptoms,
            other_symptoms = log.other_symptoms,
            user_id = user_id,
            cycle_history_id = cycle_history.id,
            phase = get_user_cycle_phase(db=db, user_id=user_id)['phase']
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return new_log

    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=422, detail="Bad Request")

    except Exception as e:
        db.rollback()
        print("Reason : ", str(e))
        raise HTTPException(status_code=500, detail="Server Error")

# get one log
def get_log_by_id(log_id : str, user_id : str, db:Session):
    try:
        log = db.query(
            DocumentationLog
        ).filter(
            DocumentationLog.id == log_id,
            DocumentationLog.user_id == user_id
        ).first()

        if log is None:
            raise HTTPException(status_code=404, detail="Log not found")

        return log

    except HTTPException:
        raise
    except Exception as e:
        print("Reason : ", str(e))
        raise HTTPException(status_code=500, detail="Server Error")


# get all logs/history
def get_history(db:Session, user_id:str):
    try:
        history = db.query(DocumentationLog).filter(DocumentationLog.user_id == user_id).all()
        return  history
    except Exception as e:
        print("Reason : ", str(e))
        raise HTTPException(status_code=500, detail="Server Error")


logger = logging.getLogger(__name__)

MIN_CYCLES = 3
MIN_RATE = 0.6


def _recurring_symptom_patterns(by_cycle: dict) -> list[dict]:
    total = len(by_cycle)
    if total < MIN_CYCLES:
        return []
    counts = Counter(item for items in by_cycle.values() for item in items)
    return [
        {"name": name, "seen_in_cycles": f"{count} of {total}"}
        for name, count in counts.most_common()
        if count / total >= MIN_RATE
    ]


def _confidence(total_cycles: int, has_patterns: bool) -> str:
    if total_cycles < MIN_CYCLES:
        return "low"
    if has_patterns and total_cycles >= 5:
        return "high"
    return "moderate"


def get_recurring_patterns(db: Session, user_id: str) -> dict:
    phase_info = get_user_cycle_phase(user_id=user_id, db=db)

    phase = phase_info["phase"]
    if hasattr(phase, "value"):
        phase = phase.value
    day = phase_info.get("day", 0)

    logs = (
        db.query(DocumentationLog)
        .filter(
            DocumentationLog.user_id == user_id,
            DocumentationLog.phase == phase,
        )
        .order_by(DocumentationLog.created_at)
        .all()
    )

    symptoms_by_cycle = defaultdict(set)
    moods_by_cycle = defaultdict(set)
    for log in logs:
        # indexing both dicts registers the cycle even if nothing was logged
        symptoms_by_cycle[log.cycle_history_id].update(
            s.strip().lower() for s in (log.symptoms or [])
        )
        moods_by_cycle[log.cycle_history_id].update(
            m.strip().lower() for m in (log.moods or [])
        )

    total_cycles = len(symptoms_by_cycle)
    recurring_symptoms = _recurring_symptom_patterns(symptoms_by_cycle)
    recurring_moods = _recurring_symptom_patterns(moods_by_cycle)

    latest_cycle = next(reversed(symptoms_by_cycle), None)

    return {
        "phase": phase,
        "day": day,
        "recurring_symptoms": recurring_symptoms,
        "recurring_moods": recurring_moods,
        "recent_symptoms": sorted(symptoms_by_cycle.get(latest_cycle, [])),
        "recent_moods": sorted(moods_by_cycle.get(latest_cycle, [])),
        "confidence": _confidence(
            total_cycles, bool(recurring_symptoms or recurring_moods)
        ),
    }
