from Models.Cycle import Cycle


def test_get_period_status_without_cycle(client):
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

    status_response = client.get("/period_log/cycle_status", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert status_response.status_code == 404
    assert status_response.json()["detail"] == "Cycle not found"


def test_get_period_status(client, db_session_fixture):
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
        "first_day_last_period": "23/10/2026",
        "estimated_end_date" : "25/10/2026",
        "period_duration": 3,
        "cycle_length": 26
    }

    cycle_response = client.post("/cycle", json=cycle_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert cycle_response.status_code == 201
    assert cycle_response.json()["id"] is not None
    assert "first_day_last_period" in cycle_response.json()

    status_response = client.get("/period_log/cycle_status", headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })

    assert status_response.status_code == 200
    db = db_session_fixture()

    cycle = db.query(Cycle).filter(Cycle.user_id == create_response.json()["id"]).first()
    assert cycle is not None

    assert "state" in status_response.json()
    assert "next_period" in status_response.json()
    assert "phase" in status_response.json()


def test_create_period_log_successful(client,db_session_fixture):
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

    log_payload ={
        "came" :True
    }

    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    json_data = log_payload_response.json()

    assert "id" in json_data is not None
    assert "start_date" in json_data is not None
    assert "estimated_end_date" in json_data
    assert "created_at" in json_data is not None

def test_create_period_log_not_authenticated(client,db_session_fixture):
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

    log_payload ={
        "came" :True
    }

    log_payload_response = client.post("/period_log", json=log_payload)
    assert log_payload_response.status_code == 401
    assert log_payload_response.json()["detail"] == "Not authenticated"


def test_confirm_period_ends(client, db_session_fixture):
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

    log_payload ={
        "came" : True
    }
    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    json_data = log_payload_response.json()

    assert "id" in json_data is not None

    payload = {
        "ended" : True,
        "actual_start_date" : "17/11/2026"
    }
    log_response = client.post("/period_log/period_ended", json=payload,
                               headers={
                                   "Authorization": f"Bearer {login_response.json()['access_token']}"
                               })
    assert log_response.status_code == 200
    assert "id" in log_response.json()
    assert isinstance(log_response.json()["id"], str)
    assert "start_date" in log_response.json()
    assert "estimated_end_date" in log_response.json()
    assert isinstance(log_response.json()["start_date"], str)


def test_confirm_period_ends_log_not_found(client, db_session_fixture):
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

    log_payload ={
        "came" : True
    }
    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    json_data = log_payload_response.json()

    assert "id" in json_data is not None

    payload = {
        "ended" : True,
        "actual_start_date" : "10/11/2026"
    }
    log_response = client.post("/period_log/period_ended", json=payload,
                               headers={
                                   "Authorization": f"Bearer {login_response.json()['access_token']}"
                               })
    assert log_response.status_code == 404
    assert log_response.json()["detail"] == "Period Log not found"


def test_confirm_period_ends_not_authenticated(client, db_session_fixture):
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

    log_payload ={
        "came" : True
    }
    log_payload_response = client.post("/period_log", json=log_payload, headers={
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    })
    assert log_payload_response.status_code == 201
    json_data = log_payload_response.json()

    assert "id" in json_data is not None

    payload = {
        "ended" : True,
        "actual_start_date" : "10/11/2026"
    }
    log_response = client.post("/period_log/period_ended", json=payload)
    assert log_response.status_code == 401
    assert log_response.json()["detail"] == "Not authenticated"

# def test_confirm_period_came(client):
#     payload = {
#         "full_name": "Jane Doe",
#         "age": 20,
#         "gender": "Female",
#         "email": "janeDoe@example.com",
#         "password": "JaneDoe@18"
#     }
#
#     create_response = client.post("/user", json=payload)
#     assert create_response.status_code == 201
#     assert isinstance(create_response.json()["id"], str)
#
#     login_payload = {
#         "email": str(payload["email"]).lower(),
#         "password": payload["password"]
#     }
#
#     login_response = client.post("/auth/login", json=login_payload)
#     assert login_response.status_code == 200
#     assert isinstance(login_response.json()["access_token"], str)
#     assert login_response.json()["token_type"] == "bearer"
#
#     cycle_payload = {
#         "first_day_last_period": "23/10/2026",
#         "estimated_end_date" : "25/10/2026",
#         "period_duration": 3,
#         "cycle_length": 26
#     }
#     cycle_response = client.post(
#         "/cycle", json=cycle_payload, headers={
#             "Authorization": f"Bearer {login_response.json()['access_token']}"
#         })
#
#     assert cycle_response.status_code == 201
#     assert "first_day_last_period" in cycle_response.json()
#
#     confirm_payload = {
#         "came" : True
#
#     }
#     status_confirmation_response = client.post("/period_log", json=confirm_payload, headers={
#         "Authorization": f"Bearer {login_response.json()['access_token']}"
#     })
#
#     assert status_confirmation_response.status_code == 201
#     assert "message" in status_confirmation_response.json()
#     assert "next_period" in status_confirmation_response.json()
#     assert status_confirmation_response.json()["next_period"] is not None
#     assert status_confirmation_response.json()["message"] is not None
#
# def test_confirm_period_not_come(client,  db_session_fixture):
#     payload = {
#         "full_name": "Jane Doe",
#         "age": 20,
#         "gender": "Female",
#         "email": "janeDoe@example.com",
#         "password": "JaneDoe@18"
#     }
#
#     create_response = client.post("/user", json=payload)
#     assert create_response.status_code == 201
#     assert isinstance(create_response.json()["id"], str)
#
#     login_payload = {
#         "email": str(payload["email"]).lower(),
#         "password": payload["password"]
#     }
#
#     login_response = client.post("/auth/login", json=login_payload)
#     assert login_response.status_code == 200
#     assert isinstance(login_response.json()["access_token"], str)
#     assert login_response.json()["token_type"] == "bearer"
#
#     cycle_payload = {
#         "first_day_last_period": "23/10/2026",
#         "period_duration": 3,
#         "cycle_length": 26
#     }
#     cycle_response = client.post(
#         "/cycle", json=cycle_payload, headers={
#             "Authorization": f"Bearer {login_response.json()['access_token']}"
#         })
#
#     assert cycle_response.status_code == 201
#     assert "first_day_last_period" in cycle_response.json()
#
#     confirm_payload = {
#         "came" : False
#     }
#     status_confirmation_response = client.post("/period_log", json=confirm_payload, headers={
#         "Authorization": f"Bearer {login_response.json()['access_token']}"
#     })
#
#     assert status_confirmation_response.status_code == 201
#     assert "message" in status_confirmation_response.json()
#     assert "state" in status_confirmation_response.json()
#     assert status_confirmation_response.json()["state"] is not None
#     assert status_confirmation_response.json()["message"] is not None

# def test_confirm_period_when_cycle_id_is_none(client):
#     payload = {
#         "full_name": "Jane Doe",
#         "age": 20,
#         "gender": "Female",
#         "email": "janeDoe@example.com",
#         "password": "JaneDoe@18"
#     }
#
#     create_response = client.post("/user", json=payload)
#     assert create_response.status_code == 201
#     assert isinstance(create_response.json()["id"], str)
#
#     login_payload = {
#         "email": str(payload["email"]).lower(),
#         "password": payload["password"]
#     }
#
#     login_response = client.post("/auth/login", json=login_payload)
#     assert login_response.status_code == 200
#     assert isinstance(login_response.json()["access_token"], str)
#     assert login_response.json()["token_type"] == "bearer"
#
#
#     confirm_payload = {
#         "came" : False
#     }
#     status_confirmation_response = client.post("/period_log", json=confirm_payload, headers={
#         "Authorization": f"Bearer {login_response.json()['access_token']}"
#     })
#
#     assert status_confirmation_response.status_code == 404
#     assert status_confirmation_response.json()["detail"] == "Cycle not found"
#
