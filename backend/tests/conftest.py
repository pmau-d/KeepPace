import os

os.environ.update(DATABASE_URL="sqlite://", ENVIRONMENT="test", COOKIE_SECURE="false")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.security import login_limiter

PASSWORD = "correct-horse-battery"


def register(api: TestClient, email: str) -> TestClient:
    response = api.post("/auth/register", json={"email": email, "password": PASSWORD})
    assert response.status_code == 201, response.text
    return api


@pytest.fixture()
def anon():
    """Client HTTP non connecté, sur une base vide."""
    Base.metadata.create_all(bind=engine)
    login_limiter.reset()
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(anon):
    """Client HTTP connecté avec un compte « alice »."""
    return register(anon, "alice@example.com")


@pytest.fixture()
def other_client(client):
    """Second compte, indépendant du premier (cookies séparés)."""
    with TestClient(app) as test_client:
        yield register(test_client, "bob@example.com")
