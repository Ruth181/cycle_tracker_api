from fastapi import FastAPI
from Models.User import User
from Models.Cycle import Cycle
from Models.Period_Log import PeriodLog
from Models.Documentation_Log import DocumentationLog
from database import Base, cycle_engine
from Routers.auth_router import auth_router
from Routers.user_router import user_router
from Routers.cycle_router import cycle_router
from Routers.period_log_router import period_log_router
from Routers.documentation_log_router import documentation_router
from Routers.notification_router import notification_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(cycle_router)
app.include_router(period_log_router)
app.include_router(documentation_router)
app.include_router(notification_router)
Base.metadata.create_all(bind=cycle_engine)

# if __name__ == "__main__":
#     import secrets
#     print(secrets.token_hex(32))