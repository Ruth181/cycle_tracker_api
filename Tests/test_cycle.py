from Models.Cycle import Cycle
from datetime import datetime

def test_create_cycle_successfully(client, db_session_fixture):
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

    db = db_session_fixture()
    cycle = db.query(Cycle).filter(
        Cycle.user_id == create_response.json()["id"],
        Cycle.id == cycle_response.json()["id"]
    ).first()

    assert cycle is not None

    assert "id" in cycle_response.json()
    assert "user_id" in cycle_response.json()
    assert "first_day_last_period" in cycle_response.json()
    assert "period_duration" in cycle_response.json()
    assert "cycle_length" in cycle_response.json()
    assert isinstance(cycle_response.json()["cycle_length"], int)
    assert isinstance(cycle_response.json()["period_duration"], int)


#update cycle when cycle_id is there
def test_update_cycle_successfully(client, db_session_fixture):
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
    assert isinstance(cycle_response.json()["id"], str)

    update_payload = {
        "first_day_last_period": "25/10/2026",
        "period_duration": 2
    }

    update_response = client.patch("/cycle", json=update_payload,
                                   headers={
                                       "Authorization": f"Bearer {login_response.json()['access_token']}"
                                   })

    assert update_response.status_code == 200

    update_db = db_session_fixture()
    update_cycle = update_db.query(Cycle).filter(Cycle.user_id == cycle_response.json()["user_id"]).first()
    assert update_cycle is not None
    assert update_cycle.first_day_last_period == datetime.strptime(str(update_payload["first_day_last_period"]), "%d/%m/%Y")
    assert update_cycle.period_duration == update_payload["period_duration"]

    assert "id" in update_response.json()
    assert "user_id" in update_response.json()
    assert "first_day_last_period" in update_response.json()
    assert "period_duration" in update_response.json()
    assert "cycle_length" in update_response.json()


# when cycle is not found
def test_update_cycle_not_found(client, db_session_fixture):
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

    update_payload = {
        "first_day_last_period": "25/10/2026",
        "period_duration": 2
    }

    update_response = client.patch("/cycle", json=update_payload,
                                   headers={
                                       "Authorization": f"Bearer {login_response.json()['access_token']}"
                                   })

    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Cycle Not Found"


def test_get_cycle_successfully(client, db_session_fixture):
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
    assert isinstance(cycle_response.json()["id"], str)

    get_cycle_response = client.get("/cycle/my-cycle", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 200
    db = db_session_fixture()
    cycle = db.query(Cycle).filter(Cycle.user_id == cycle_response.json()["user_id"]).first()
    assert cycle is not None

    assert "id" in cycle_response.json()
    assert "first_day_last_period" in cycle_response.json()
    assert "period_duration" in cycle_response.json()
    assert "cycle_length" in cycle_response.json()
    assert isinstance(cycle_response.json()["cycle_length"], int)
    assert isinstance(cycle_response.json()["period_duration"], int)



def test_get_cycle_not_found(client, db_session_fixture):
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


    get_cycle_response = client.get("/cycle/my-cycle", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 404
    assert get_cycle_response.json()["detail"] == "User cycle not found"


def test_cycle_status_successfully(client, db_session_fixture):
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
    assert isinstance(cycle_response.json()["id"], str)


    get_cycle_response = client.get("/cycle/stats", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 200
    db = db_session_fixture()
    cycle = db.query(Cycle).filter(Cycle.user_id == cycle_response.json()["user_id"]).first()
    assert cycle is not None

    assert "next_period" in get_cycle_response.json()
    assert "ovulation" in get_cycle_response.json()
    assert "fertile_window" in get_cycle_response.json()
    assert "start" in get_cycle_response.json()["fertile_window"]
    assert "end" in get_cycle_response.json()["fertile_window"]
    assert "follicular" in get_cycle_response.json()
    assert "start" in get_cycle_response.json()["follicular"]
    assert "end" in get_cycle_response.json()["follicular"]
    assert "luteal" in get_cycle_response.json()
    assert "start" in get_cycle_response.json()["luteal"]
    assert "end" in get_cycle_response.json()["luteal"]


def test_cycle_status_not_found(client, db_session_fixture):
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



    get_cycle_response = client.get("/cycle/stats", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 404
    assert  get_cycle_response.json()["detail"] == "User cycle not found"


def test_cycle_phase_successfully(client, db_session_fixture):
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
    assert isinstance(cycle_response.json()["id"], str)


    get_cycle_response = client.get("/cycle/cycle-phase", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 200
    db = db_session_fixture()
    cycle = db.query(Cycle).filter(Cycle.user_id == cycle_response.json()["user_id"]).first()
    assert cycle is not None

    assert "message" in get_cycle_response.json()
    assert "is_fertile" in get_cycle_response.json()
    assert isinstance(get_cycle_response.json()["is_fertile"], bool)
    assert "phase" in get_cycle_response.json()


def test_cycle_phase_not_found(client, db_session_fixture):
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


    get_cycle_response = client.get("/cycle/cycle-phase", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 404
    assert get_cycle_response.json()["detail"] == "User cycle not found"


def test_predict_user_cycle_successfully(client, db_session_fixture):
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
    assert isinstance(cycle_response.json()["id"], str)

    get_cycle_response = client.get("/cycle/predict/6-months", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 200
    db = db_session_fixture()
    cycle = db.query(Cycle).filter(Cycle.user_id == cycle_response.json()["user_id"]).first()
    assert cycle is not None

    data = get_cycle_response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for cycle in data:
        assert "cycle_number" in cycle
        assert "period" in cycle
        assert "start" in cycle["period"]
        assert "end" in cycle["period"]
        assert "fertile_window" in cycle
        assert "start" in cycle["fertile_window"]
        assert "end" in cycle["fertile_window"]
        assert "ovulation_date" in cycle
        assert "next_period_preview" in cycle



def test_predict_user_cycle_not_found(client, db_session_fixture):
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

    get_cycle_response = client.get("/cycle/predict/6-months", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert get_cycle_response.status_code == 404
    assert get_cycle_response.json()["detail"] == "User cycle not found"



