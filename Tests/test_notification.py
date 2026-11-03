from Models.Cycle import Cycle
from datetime import datetime

#successfully
def test_patch_notification(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com",
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None

    login_payload = {
        "email": str(payload["email"]).lower(),
        "password": payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    cycle_payload = {
        "first_day_last_period" : "23/10/2026",
        "period_duration" : 3,
        "cycle_length" : 26
    }

    cycle_response = client.post("/cycle", json=cycle_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert cycle_response.status_code == 201
    assert cycle_response.json()["id"] is not None
    assert "first_day_last_period" in cycle_response.json()

    notification_response = client.get("/notification", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert notification_response.status_code == 200

    db = db_session_fixture()

    cycle = db.query(Cycle).filter(Cycle.user_id == create_response.json()["id"]).first()
    assert cycle is not None


    assert "notify" in notification_response.json()
    assert "message" in notification_response.json()


#cycle not found
def test_patch_notification_cycle_not_found(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com",
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None

    login_payload = {
        "email": str(payload["email"]).lower(),
        "password": payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"


    notification_response = client.get("/notification", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert notification_response.status_code == 404
    assert notification_response.json()["detail"] == "Cycle not found"


#get notifications without token

def test_notification_without_token(client):
    notification_response = client.get("/notification")

    assert notification_response.status_code == 401
    assert notification_response.json()["detail"] == "Not authenticated"