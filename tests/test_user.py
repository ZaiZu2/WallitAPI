from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import api.schemas as s
from tests.conftest import TestUser, get_test_access_token_header


def test_token(client: TestClient, db: Session) -> None:
    user_1 = TestUser("EUR")
    db.add(user_1)
    db.commit()

    # correct credentials
    response = client.post(
        "/token",
        data={
            "username": user_1.username,
            "password": f"password{user_1.instance_number}",
        },
    )
    assert response.status_code == 200

    # wrong password
    response = client.post(
        "/token",
        data={
            "username": user_1.username,
            "password": "wrong",
        },
    )
    assert response.status_code == 404


def test_current_user(client: TestClient, db: Session) -> None:
    user_1 = TestUser("EUR")
    db.add(user_1)
    db.commit()

    # correct token
    response = client.get("/user", headers=get_test_access_token_header(client, user_1))
    assert response.status_code == 200
    assert response.json() == s.User.from_orm(user_1).dict()

    # wrong token
    response = client.get("/user", headers={"Authorization": f"Bearer wrong"})
    assert response.status_code == 401


def test_create_user(client: TestClient) -> None:
    user_1 = TestUser("EUR")
    user_2 = TestUser("EUR")

    # correct data
    response = client.post(
        "/user",
        json=dict(
            username=user_1.username,
            email=user_1.email,
            password=f"password{user_1.instance_number}",
            first_name=user_1.first_name,
            last_name=user_1.last_name,
            main_currency=user_1.main_currency,
        ),
    )
    assert response.status_code == 201
    assert response.json() == s.User.from_orm(user_1).dict()

    # user already created with the same username
    response = client.post(
        "/user",
        json=dict(
            username=user_1.username,  # Pre-existing user
            email=user_2.email,
            password=f"password{user_2.instance_number}",
            first_name=user_2.first_name,
            last_name=user_2.last_name,
            main_currency=user_2.main_currency,
        ),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Username is already used"

    # user already created with the same email
    response = client.post(
        "/user",
        json=dict(
            username=user_2.username,
            email=user_1.email,  # Pre-existing user
            password=f"password{user_2.instance_number}",
            first_name=user_2.first_name,
            last_name=user_2.last_name,
            main_currency=user_2.main_currency,
        ),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "E-mail address is already used"


def test_modify_current_user(client: TestClient, db: Session) -> None:
    user_1 = TestUser("CZK")
    db.add(user_1)
    db.commit()
    header = get_test_access_token_header(client, user_1)

    # correct data
    body_1 = dict(
        first_name="changed_first_1", last_name="changed_last_1", main_currency="USD"
    )
    response = client.put(
        "/user",
        headers=header,
        json=body_1,
    )
    assert response.status_code == 200
    assert response.json().items() >= body_1.items()

    # correct partial data
    body_2 = dict(first_name="changed_first_2")
    response = client.put(
        "/user",
        headers=header,
        json=body_2,
    )
    assert response.status_code == 200
    assert response.json().items() >= body_2.items()

    # incorrect extra fields
    body_3 = dict(username="changed_username_3", email="changed_3@gmail.com")
    response = client.put(
        "/user",
        headers=header,
        json=body_3,
    )
    assert response.status_code == 422
    assert response.json()["details"]["username"] == "extra fields not permitted"


def test_change_password(client: TestClient, db: Session) -> None:
    user_1 = TestUser("CZK")
    db.add(user_1)
    db.commit()
    header = get_test_access_token_header(client, user_1)

    # correct data
    body_1 = dict(
        old_password=f"password{user_1.instance_number}",
        new_password="changed_password",
        repeat_password="changed_password",
    )
    response = client.put(
        "/user/password",
        headers=header,
        json=body_1,
    )
    assert response.status_code == 200

    # passwords do not match
    body_2 = dict(
        old_password=f"password{user_1.instance_number}",
        new_password="changed_password",
        repeat_password="wrong_password",
    )
    response = client.put("/user/password", headers=header, json=body_2)
    assert response.status_code == 422
    assert response.json()["details"]["repeat_password"] == "Passwords do not match"

    # incomplete body
    body_3 = dict(
        old_password=f"password{user_1.instance_number}",
        new_password="changed_password",
    )
    response = client.put("/user/password", headers=header, json=body_3)
    assert response.status_code == 422
    assert response.json()["details"]["repeat_password"] == "field required"
