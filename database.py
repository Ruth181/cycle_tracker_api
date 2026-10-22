from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

cycle_engine = create_engine(
    url=settings.database_url
)

@event.listens_for(cycle_engine, "connect")
def enable_foreign_keys_session(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cycle_engine)

def get_db_session():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


