import os

# SQLite en mémoire par défaut ; TEST_DATABASE_URL permet de viser PostgreSQL (CI).
os.environ.update(
    DATABASE_URL=os.environ.get("TEST_DATABASE_URL", "sqlite://"), ENVIRONMENT="test", COOKIE_SECURE="false"
)

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.security import login_limiter, public_limiter

PASSWORD = "correct-horse-battery"


def register(api: TestClient, username: str) -> TestClient:
    response = api.post("/auth/register", json={"username": username, "password": PASSWORD})
    assert response.status_code == 201, response.text
    return api


@pytest.fixture()
def anon():
    """Client HTTP non connecté, sur une base vide."""
    Base.metadata.create_all(bind=engine)
    login_limiter.reset()
    public_limiter.reset()
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(anon):
    """Client HTTP connecté avec un compte « alice »."""
    return register(anon, "alice")


@pytest.fixture()
def other_client(client):
    """Second compte, indépendant du premier (cookies séparés)."""
    with TestClient(app) as test_client:
        yield register(test_client, "bob")
