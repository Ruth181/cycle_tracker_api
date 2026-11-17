from Models.CycleHistory import CycleHistory
from datetime import datetime

def test_cycle_history_successful(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com",
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert isinstance(create_response.json()["id"], str)

    login_payload = {
        "email": str(payload["email"]).lower(),
        "password": payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    log_payload = {
        "came": True
    }

    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    assert isinstance(log_payload_response.json()["id"], str)

    cycle_payload = {
        "first_day_last_period": "23/10/2026",
        "period_duration": 3,
        "cycle_length": 26
    }
    cycle_response = client.post(
        "/cycle", json=cycle_payload, headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        })

    assert cycle_response.status_code == 201

    new_cycle = CycleHistory(
        user_id=create_response.json()["id"],
        start_date=datetime.strptime("10/10/2026", "%d/%m/%Y"),
        period_log_id=log_payload_response.json()["id"]
    )
    db = db_session_fixture()
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)

    assert new_cycle is not None
    assert new_cycle.id is not None
    assert isinstance(new_cycle.id, str)
    assert isinstance(new_cycle.start_date, datetime)



def test_get_cycle_history_successful(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com",
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert isinstance(create_response.json()["id"], str)

    login_payload = {
        "email": str(payload["email"]).lower(),
        "password": payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    log_payload = {
        "came": True
    }

    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    assert isinstance(log_payload_response.json()["id"], str)

    cycle_payload = {
        "first_day_last_period": "23/10/2026",
        "period_duration": 3,
        "cycle_length": 26
    }
    cycle_response = client.post(
        "/cycle", json=cycle_payload, headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        })

    assert cycle_response.status_code == 201

    new_cycle = CycleHistory(
        user_id=create_response.json()["id"],
        start_date=datetime.strptime("10/10/2026", "%d/%m/%Y"),
        period_log_id=log_payload_response.json()["id"]
    )
    db = db_session_fixture()
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)

    assert new_cycle is not None
    assert new_cycle.id is not None
    assert isinstance(new_cycle.id, str)
    assert isinstance(new_cycle.start_date, datetime)


    histories = client.get("/cycle-history", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert histories.status_code == 200
    data = histories.json()

    assert len(data) > 0

    for doc in data:
        assert isinstance(doc["id"], str)
        assert isinstance(doc["user_id"], str)
        assert isinstance(doc["start_date"], datetime)
        assert isinstance(doc["end_date"], datetime | None)
        assert isinstance(doc["period_log_id"], str)
        assert isinstance(doc["created_at"], datetime)


def test_get_cycle_history_not_authenticated(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com",
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert isinstance(create_response.json()["id"], str)

    login_payload = {
        "email": str(payload["email"]).lower(),
        "password": payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    log_payload = {
        "came": True
    }

    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    assert isinstance(log_payload_response.json()["id"], str)

    cycle_payload = {
        "first_day_last_period": "23/10/2026",
        "period_duration": 3,
        "cycle_length": 26
    }
    cycle_response = client.post(
        "/cycle", json=cycle_payload, headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        })

    assert cycle_response.status_code == 201

    new_cycle = CycleHistory(
        user_id=create_response.json()["id"],
        start_date=datetime.strptime("10/10/2026", "%d/%m/%Y"),
        period_log_id=log_payload_response.json()["id"]
    )
    db = db_session_fixture()
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)

    assert new_cycle is not None
    assert new_cycle.id is not None
    assert isinstance(new_cycle.id, str)
    assert isinstance(new_cycle.start_date, datetime)


    histories = client.get("/cycle-history")

    assert histories.status_code == 401
    assert histories.json()["detail"] == "Not authenticated"


