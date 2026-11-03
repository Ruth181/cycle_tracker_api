from security import verify_password
from Models.User import User
#from unittest.mock import patch
from Services import auth_service

#test login successfully
def test_login(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com".lower(),
        "password": "JaneDoe@18"
    }

    create_response =client.post("/user", json=payload)
    assert create_response.status_code == 201

    db_confirm = db_session_fixture()
    try:
        user = db_confirm.query(User).filter(User.id == create_response.json()["id"]).first()
        assert user.email == payload["email"]
        assert verify_password(str(payload["password"]), user.password_hash) == True

    finally:
        db_confirm.close()

    assert isinstance(create_response.json()["id"], str)
    assert create_response.json()["full_name"] == payload["full_name"]

    login_response = client.post("/auth/login", json={
        "email": str(payload["email"]).lower(),
        "password":payload["password"]
    })

    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"


#test login with invalid cred
def test_login_with_invalid_email(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com".lower(),
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None

    login_payload = {
        "email": "johnsmith@gmail.com",
        "password": "JohnSmith@45"
    }

    login_response = client.post("/auth/login", json=login_payload)
    db_confirm = db_session_fixture()
    try:
        user = db_confirm.query(User).filter(User.email == login_payload["email"]).first()
        assert user is None
    finally:
        db_confirm.close()

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid Credentials"



def test_login_with_incorrect_password(client, db_session_fixture):
    payload = {
        "full_name": "Jane Doe",
        "age": 20,
        "gender": "Female",
        "email": "janeDoe@example.com".lower(),
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None

    login_payload = {
        "email": str(payload["email"]).lower(),
        "password": "JohnSmith@45"
    }

    login_response = client.post("/auth/login", json=login_payload)
    db_confirm = db_session_fixture()
    try:
        user = db_confirm.query(User).filter(User.email == login_payload["email"]).first()
        assert user is not None
        assert verify_password(str(login_payload["password"]), user.password_hash) == False

    finally:
        db_confirm.close()

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid Credentials"



FAKE_CLAIMS = {
    "sub": "google-123",
    "email": "test@example.com",
    "email_verified": True,
    "name": "Test User",
}

def patch_google(monkeypatch, claims):
    monkeypatch.setattr(auth_service, "google_auth", lambda token: claims)

#test google credentials
# def test_new_user_is_created(client, db_session_fixture, monkeypatch):
#     patch_google(monkeypatch, FAKE_CLAIMS)
#
#     res = client.post("/google-login", json={"id_token": "fake"})
#
#     assert res.status_code == 200
#     assert "access_token" in res.json()
#
#     db = db_session_fixture()
#     try:
#         user = db.query(User).filter(User.email == "test@example.com").first()
#     finally:
#         db.close()
#
#     assert user is not None
#     assert user.google_sub == "google-123"


# def test_existing_email_is_linked(client, db_session_fixture, monkeypatch):
#     # Pre-create a user who signed up another way (no google_sub yet)
#     db = db_session_fixture()
#     try:
#         db.add(User(email="test@example.com", full_name="Old Name"))
#         db.commit()
#     finally:
#         db.close()
#
#     patch_google(monkeypatch, FAKE_CLAIMS)
#
#     res = client.post("/google-login", json={"id_token": "fake"})
#
#     assert res.status_code == 200
#     assert db.query(User).filter(User.email == "test@example.com").count() == 1  # no duplicate
#     user = db.query(User).filter(User.email == "test@example.com").first()
#     assert user.google_sub == "google-123"


# def test_returning_google_user(client, db_session_fixture, monkeypatch):
#     db = db_session_fixture()
#     try:
#         db.add(User(email="test@example.com", google_sub="google-123"))
#         db.commit()
#     finally:
#         db.close()
#
#     patch_google(monkeypatch, FAKE_CLAIMS)
#
#     res = client.post("/google-login", json={"id_token": "fake"})
#
#     assert res.status_code == 200


# def test_unverified_email_rejected(client, monkeypatch):
#     patch_google(monkeypatch, {**FAKE_CLAIMS, "email_verified": False})
#
#     res = client.post("/google-login", json={"id_token": "fake"})
#
#     assert res.status_code == 400


# def test_new_google_incorrect_user(client):
#     with patch("Services.auth_service.google_auth") as mock_verify:
#         mock_verify.return_value = {"sub": "123", "email": "a@b.com", "email_verified": True}
#         res = client.post("/google-login", json={"id_token": "fake"})
#         assert res.status_code == 404
#         assert res.json() == {"detail": "Not Found"}