from Models.User import User
from security import verify_password


fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkxMjA5NTEzfQ.OFI5lTu1hFJPsyAb57JGvj2Q8SSNsHimUshAaLtZ73E"
# User
#  create-user successfully
def test_create_user(client, db_session_fixture):
    payload ={
        "full_name": "Jane Smith",
        "age": 18,
        "gender": "Female",
        "email": "jane@example.com",
        "password": "JaneSmith@18"
    }

    #make the api request
    response = client.post("/user", json=payload)

    assert response.status_code == 201
    #check that the email exists in the db
    db = db_session_fixture()
    try:
        user = db.query(User).filter(User.email == payload["email"]).first()

        assert user is not None
        assert verify_password(str(payload["password"]), user.password_hash) == True

    finally:
        db.close()

    json_response = response.json()

    assert json_response["full_name"] == payload["full_name"]
    assert json_response["id"] is not None
    assert json_response["email"] == str(payload["email"]).lower()


#create user with used email
def test_with_already_existing_account(client,db_session_fixture):
    payload = {
        "full_name": "Jane Smith",
        "age": 18,
        "gender": "Female",
        "email": "jane@example.com",
        "password": "JaneSmith@18"
    }

    create_response = client.post("/user", json=payload)

    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None

    fail_user_response = client.post("/user", json=payload)
    assert fail_user_response.status_code == 409
    assert fail_user_response.json()["detail"] == "user already exists"

    normalized_email =  str(payload["email"]).lower()
    db_confirm = db_session_fixture()
    try:
        user = db_confirm.query(User).filter(User.email == normalized_email).count()
        assert user == 1
    finally:
        db_confirm.close()

#  update-user == when all goes well
def test_update_user(client, db_session_fixture):
    payload = {
        "full_name": "Jane Smith",
        "age": 18,
        "gender": "Female",
        "email": "jane@example.com",
        "password": "JaneSmith@18"
    }
    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None
    assert create_response.json()["email"] == str(payload["email"]).lower()

    #login to get token

    login_payload = {
        "email" : str(payload["email"]).lower(),
        "password" : payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    update_payload = {
        "full_name": "Jamie Smith",
        "age": 26,
        "gender": "Male"
    }
    print("login", login_response.json()['access_token'])
    update_response = client.patch("/user/me", json=update_payload, headers={
        "Authorization" : f"Bearer {login_response.json()['access_token']}"
    })

    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == update_payload["full_name"]
    assert update_response.json()["age"] == update_payload["age"]
    assert update_response.json()["gender"] == update_payload["gender"]

# update_user when the user token is wrong
def test_update_user_with_invalid_token(client, db_session_fixture):
    update_payload = {
        "full_name": "Jane Smith"
    }

    update_response = client.patch("/user/me", json=update_payload, headers={
        "Authorization" : f"Bearer {fake_token}"
    })

    assert update_response.status_code == 401
    assert update_response.json()["detail"] == "Invalid Token"

# update_user when the user_id is wrong
# def test_update_user_with_invalid_user_id(client, db_session_fixture):
#     payload = {
#         "full_name" : "Jane Doe",
#         "age" : 20,
#         "gender": "Female",
#         "email": "janeDoe@example.com",
#         "password": "JaneDoe@18"
#     }
#     create_response = client.post("/user", json=payload)
#     assert create_response.status_code == 201
#     assert create_response.json()["id"] is not None
#
#     login_payload = {
#         "email": "janeDoe@example.com",
#         "password": "JaneDoe@18"
#     }
#
#     login_response = client.post("/auth/login", json=login_payload)
#     assert login_response.status_code == 200
#     assert isinstance(login_response.json()["access_token"], str)
#     assert login_response.json()["token_type"] == "bearer"
#
#     update_payload = {
#         "full_name": "Jane Smith"
#     }
#
#     update_response = client.patch("/user/me", json=update_payload, headers={
#         "Authorization" : f"Bearer {login_response.json()['access_token']}"
#     })
#     db = db_session_fixture()
#     try:
#         user = db.query(User).filter(User.id == 1).first()
#         assert user is None
#     finally:
#         db.close()
#
#     assert update_response.status_code == 404
#     assert update_response.json()["detail"] == "User not found"


#  get user successfully
def test_get_user_successfully(client):
    payload = {
        "full_name" : "Jane Doe",
        "age" : 20,
        "gender": "Female",
        "email": "janeDoe@example.com",
        "password": "JaneDoe@18"
    }

    create_response = client.post("/user", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] is not None

    login_payload = {
        "email" : str(payload["email"]).lower(),
        "password" : payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    user_response = client.get("/user/me", headers={
        "Authorization" : f"Bearer {login_response.json()['access_token']}"
    })

    assert user_response.status_code == 200
    assert isinstance(user_response.json()["id"], str)
    assert isinstance(user_response.json()["full_name"], str)
    assert isinstance(user_response.json()["age"], int)
    assert isinstance(user_response.json()["gender"], str)
    assert user_response.json()["email"] == str(payload["email"]).lower()


#  get user with bad token
def test_get_user_with_invalid_token(client):
    user_response = client.get("/user/me", headers={
        'Authorization' : f"Bearer {fake_token}"
    })

    assert user_response.status_code == 401
    assert user_response.json()["detail"] == "Invalid Token"


#  get user without token
def test_get_user_with_authentication(client):
    user_response = client.get("/user/me")

    assert user_response.status_code == 401
    assert user_response.json()["detail"] == "Not authenticated"


#  delete-user,successfully
def test_delete_user_successfully(client, db_session_fixture):
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
        "email" : str(payload["email"]).lower(),
        "password" : payload["password"]
    }

    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert isinstance(login_response.json()["access_token"], str)
    assert login_response.json()["token_type"] == "bearer"

    delete_response = client.delete("/user/me", headers={
        "Authorization" : f"Bearer {login_response.json()['access_token']}"
    })

    assert delete_response.status_code == 204

    db_confirm = db_session_fixture()
    try:
        user = db_confirm.query(User).filter(User.id == create_response.json()["id"]).first()
        assert user is None
    finally:
        db_confirm.close()


#delete without token
def test_delete_without_token(client):
    delete_response = client.delete("/user/me")

    assert delete_response.status_code == 401
    assert delete_response.json()["detail"] == "Not authenticated"


#delete with invalid token
def test_delete_with_invalid_token(client):
    delete_response = client.delete("/user/me", headers={
        "Authorization" : f"Bearer {fake_token}"
    })

    assert delete_response.status_code == 401
    assert delete_response.json()["detail"] == "Invalid Token"
