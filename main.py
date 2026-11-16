from fastapi import FastAPI
from Models.User import User
from Models.Cycle import Cycle
from Models.Period_Log import PeriodLog
from Models.Documentation_Log import DocumentationLog
from Models.CycleHistory import CycleHistory
from database import Base, cycle_engine
from Routers.auth_router import auth_router
from Routers.user_router import user_router
from Routers.cycle_router import cycle_router
from Routers.period_log_router import period_log_router
from Routers.documentation_log_router import documentation_router
from Routers.notification_router import notification_router
from Routers.cycle_history_router import cycle_history_router
from Routers.llm_router import llm_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(cycle_router)
app.include_router(period_log_router)
app.include_router(documentation_router)
app.include_router(notification_router)
app.include_router(cycle_history_router)
app.include_router(llm_router)
Base.metadata.create_all(bind=cycle_engine)


#if __name__ == "__main__":
#     import secrets
#     print(secrets.token_hex(32))

# from Services.llm_service import generate_daily_message
#
# result = generate_daily_message({
#     "phase": "Luteal", "day": 23,
#     "recurring_symptoms": [], "recurring_moods": [],
#     "recent_symptoms": ["slight headaches", "waist pain"],
#     "recent_moods": ["annoyed", "dreary", "frustrated"],
#     "confidence": "low",
# })
# print("LLM_RESULT ",result)