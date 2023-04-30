from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import api.schemas as s
from tests.conftest import ModelFactory, get_test_access_token_header


def test_create_category(
    client: TestClient, db: Session, model_factory: ModelFactory
) -> None:
    user_1 = model_factory.create_user("EUR")
    category_1 = model_factory.create_category(user_1)
    db.add_all([user_1, category_1])
    db.commit()
    header = get_test_access_token_header(client, user_1)

    # data already exists - conflict
    body_1 = {"name": category_1.name}
    response = client.post("categories/", headers=header, json=body_1)
    assert response.status_code == 409

    # correct data
    body_2 = {"name": "Correct"}
    response = client.post("categories/", headers=header, json=body_2)
    assert response.status_code == 201
    assert response.json().items() >= body_2.items()

    # incorrect data
    body_3 = {"name": "!@?@!#"}
    response = client.post("categories/", headers=header, json=body_3)
    assert response.status_code == 422
    assert response.json()["body"]["name"] == [
        "String must only contain Unicode letters"
    ]


def test_get_category(
    client: TestClient, db: Session, model_factory: ModelFactory
) -> None:
    user_1 = model_factory.create_user("EUR")
    user_2 = model_factory.create_user("EUR")
    category_1 = model_factory.create_category(user_1)
    category_2 = model_factory.create_category(user_2)
    db.add_all([user_1, user_2, category_1, category_2])
    db.commit()
    header = get_test_access_token_header(client, user_1)

    # correct data
    response = client.get(f"categories/{category_1.id}", headers=header)
    assert response.status_code == 200
    assert response.json() == s.Category.from_orm(category_1)

    # incorrect data
    response = client.get("categories/432", headers=header)
    assert response.status_code == 404

    # incorrect path param
    response = client.get("categories/asdew", headers=header)
    assert response.status_code == 422
    assert response.json()["path"]["id"] == ["value is not a valid integer"]

    # category not owned by the querying user
    response = client.get(f"categories/{category_2.id}", headers=header)
    assert response.status_code == 404


def test_modify_category(
    client: TestClient, db: Session, model_factory: ModelFactory
) -> None:
    user_1 = model_factory.create_user("EUR")
    user_2 = model_factory.create_user("EUR")
    category_1 = model_factory.create_category(user_1)
    category_2 = model_factory.create_category(user_2)
    db.add_all([user_1, user_2, category_1, category_2])
    db.commit()
    header = get_test_access_token_header(client, user_1)

    # correct data
    body_1 = {"name": "categoryNew"}
    response = client.put(f"categories/{category_1.id}", headers=header, json=body_1)
    assert response.status_code == 200
    assert response.json().items() >= body_1.items()

    # incorrect data
    body_2 = {"name": "!@#$@!"}
    response = client.put(f"categories/{category_1.id}", headers=header, json=body_2)
    assert response.status_code == 422
    assert response.json()["body"]["name"] == [
        "String must only contain Unicode letters"
    ]

    # incorrect path param
    response = client.put("categories/asdew", headers=header, json=body_1)
    assert response.status_code == 422
    assert response.json()["path"]["id"] == ["value is not a valid integer"]

    # category not owned by the querying user
    body_3 = {"name": "categoryNew"}
    response = client.put(f"categories/{category_2.id}", headers=header, json=body_3)
    assert response.status_code == 404


def test_delete_category(
    client: TestClient, db: Session, model_factory: ModelFactory
) -> None:
    user_1 = model_factory.create_user("EUR")
    user_2 = model_factory.create_user("EUR")
    category_1 = model_factory.create_category(user_1)
    category_2 = model_factory.create_category(user_2)
    db.add_all([user_1, user_2, category_1, category_2])
    db.commit()
    header = get_test_access_token_header(client, user_1)

    # correct data
    response = client.delete(f"categories/{category_1.id}", headers=header)
    assert response.status_code == 204

    # incorrect path param
    response = client.delete("categories/asdew", headers=header)
    assert response.status_code == 422
    assert response.json()["path"]["id"] == ["value is not a valid integer"]

    # category not owned by the querying user
    response = client.delete(f"categories/{category_2.id}", headers=header)
    assert response.status_code == 404
