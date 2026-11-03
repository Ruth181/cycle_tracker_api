import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from Dependencies.auth_dependency import get_db_session
from database import Base
from fastapi.testclient import TestClient

@pytest.fixture
def db_engine_fixture(tmp_path):
     path = tmp_path / "test_cycle_tracker.db"

     test_engine = create_engine(
         url=f"sqlite:///{path}",
         connect_args={"check_same_thread": False}
     )

     try:
         yield test_engine

     finally:
         test_engine.dispose()



@pytest.fixture
def db_session_fixture(db_engine_fixture):
    test_session_factory = sessionmaker(
        bind=db_engine_fixture,
        autocommit=False,
        autoflush=False,
    )

    def override_get_db_session():
        db_test = test_session_factory()

        try:
            yield db_test
        finally:
            db_test.close()

    app.dependency_overrides[get_db_session] = override_get_db_session
    Base.metadata.create_all(db_engine_fixture)

    try:
        yield test_session_factory

    finally:
        app.dependency_overrides[get_db_session] = get_db_session
        Base.metadata.drop_all(db_engine_fixture)




@pytest.fixture
def client(db_session_fixture):
    # Provide a client for making api requests
    with TestClient(app) as test_client:
        yield test_client

