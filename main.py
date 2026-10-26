from fastapi import FastAPI
from Models.User import User
from Models.Cycle import Cycle
from Models.Period_Log import PeriodLog
from database import Base, cycle_engine
from Routers.auth_router import auth_router
from Routers.user_router import user_router
from Routers.cycle_router import cycle_router
from Routers.period_log_router import period_log_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(cycle_router)
app.include_router(period_log_router)
Base.metadata.create_all(bind=cycle_engine)

@app.get("/")
def read_root():
    return {"message : Hello App"}

# if __name__ == "__main__":
#     import secrets
#     print(secrets.token_hex(32))