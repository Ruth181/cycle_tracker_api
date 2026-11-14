from Models.Documentation_Log import DocumentationLog

def test_create_documentation_log_success(client, db_session_fixture):
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

    doc_payload = {
        "is_period" : False,
        "symptoms" : [
            "Lightheaded",
            "Headaches",
            "low energy"
        ]
    }
    doc_response = client.post("/doc_logs", json=doc_payload,
                               headers={"Authorization": f"Bearer {login_response.json()['access_token']}"})
    assert doc_response.status_code == 201

    db = db_session_fixture()
    doc_log = db.query(DocumentationLog).filter(DocumentationLog.id == doc_response.json()["id"]).first()
    assert doc_log.symptoms == doc_payload["symptoms"]
    assert doc_log.is_period == doc_payload["is_period"]
    assert doc_log.user_id == create_response.json()["id"]

    assert isinstance(doc_response.json()["id"], str)
    assert doc_response.json()["symptoms"] == doc_payload["symptoms"]
    assert isinstance(doc_response.json()["is_period"], bool)


def test_get_log_by_id(client, db_session_fixture):
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

    doc_payload = {
        "is_period": False,
        "symptoms": [
            "Lightheaded",
            "Headaches",
            "low energy"
        ]
    }
    doc_response = client.post("/doc_logs", json=doc_payload,
                               headers={"Authorization": f"Bearer {login_response.json()['access_token']}"})
    assert doc_response.status_code == 201
    assert isinstance(doc_response.json()["id"], str)

    get_log = client.get(f"/doc_logs/{doc_response.json()['id']}",
                         headers={"Authorization": f"Bearer {login_response.json()['access_token']}"})

    assert get_log.status_code == 200
    db = db_session_fixture()
    is_log = db.query(DocumentationLog).filter(DocumentationLog.id == doc_response.json()["id"]).first()
    assert is_log is not None

    assert get_log.json()["symptoms"] is not None
    assert get_log.json()["is_period"] is not None
    assert isinstance(get_log.json()["is_period"], bool)


def test_get_log_by_id_not_authenticated(client, db_session_fixture):
    get_log = client.get("/doc_logs")

    assert get_log.status_code == 401
    assert get_log.json()["detail"] == "Not authenticated"


def test_get_log_by_id_not_found(client, db_session_fixture):
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

    get_log = client.get(f"/doc_logs/{create_response.json()['id']}",
                         headers={"Authorization": f"Bearer {login_response.json()['access_token']}"})

    assert get_log.status_code == 404
    assert get_log.json()["detail"] == "Log not found"


def test_history_success(client):
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

    doc_payload = {
        "is_period": False,
        "symptoms": [
            "Lightheaded",
            "Headaches",
            "low energy"
        ]
    }
    doc_response = client.post("/doc_logs", json=doc_payload,
                               headers={"Authorization": f"Bearer {login_response.json()['access_token']}"})
    assert doc_response.status_code == 201

    get_history_response = client.get("/doc_logs", headers=
    {"Authorization": f"Bearer {login_response.json()['access_token']}"})

    assert get_history_response.status_code == 200
    assert isinstance(get_history_response.json(), list)

    history = get_history_response.json()
    assert len(history) > 0

    for doc in history:
        assert isinstance(doc["id"], str)
        assert isinstance(doc["user_id"], str)
        assert isinstance(doc["is_period"], bool)
        assert isinstance(doc["symptoms"], list)
        assert isinstance(doc["other_symptoms"], str | None)


def test_get_history_not_authenticated(client):
    get_history_response = client.get("/doc_logs")

    assert get_history_response.status_code == 401
    assert get_history_response.json()["detail"] == "Not authenticated"



