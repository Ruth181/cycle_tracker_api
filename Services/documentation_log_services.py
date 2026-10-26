from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Documentation_Log import DocumentationLog
from Schemas.documentation_log_schema import ReqDocumentationLog


# get notifications
# get symptoms

# create logs and get history
def add_new_log(log:ReqDocumentationLog, user_id:str, db:Session):
    try:
        new_log = DocumentationLog(
            is_period = log.is_period,
            flow_intensity = log.flow_intensity,
            symptoms = log.symptoms,
            other_symptoms = log.other_symptoms,
            user_id = user_id
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


