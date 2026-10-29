from sqlalchemy import text

from app.config import settings
from app.database import engine
from tests.conftest import PASSWORD


def test_api_requires_authentication(anon):
    for path in ("/tasks/", "/clients/", "/companies/", "/auth/me"):
        assert anon.get(path).status_code == 401


def test_register_login_logout_with_a_username(anon):
    created = anon.post("/auth/register", json={"username": "Alice", "password": PASSWORD})
    assert created.status_code == 201
    assert created.json()["username"] == "alice"
    assert created.json()["email"] is None
    cookie = created.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie

    assert anon.post("/auth/logout").status_code == 204
    assert anon.get("/auth/me").status_code == 401

    assert anon.post("/auth/login", json={"username": "alice", "password": "nope"}).status_code == 401
    # Insensible à la casse
    assert anon.post("/auth/login", json={"username": "ALICE", "password": PASSWORD}).status_code == 200
    assert anon.get("/auth/me").json()["username"] == "alice"


def test_email_is_optional_and_still_works_to_log_in(anon):
    created = anon.post(
        "/auth/register", json={"username": "bob", "email": "Bob@Example.com", "password": PASSWORD}
    )
    assert created.json()["email"] == "bob@example.com"
    anon.post("/auth/logout")
    assert (
        anon.post("/auth/login", json={"username": "bob@example.com", "password": PASSWORD}).status_code
        == 200
    )
    # L'ancien champ « email » de l'API reste accepté
    anon.post("/auth/logout")
    assert anon.post("/auth/login", json={"email": "bob", "password": PASSWORD}).status_code == 200


def test_username_must_be_simple_and_unique(anon):
    for bad in ("ab", "avec espace", "a" * 33, "é/è"):
        response = anon.post("/auth/register", json={"username": bad, "password": PASSWORD})
        assert response.status_code == 422, bad
    assert anon.post("/auth/register", json={"username": "alice", "password": PASSWORD}).status_code == 201
    assert anon.post("/auth/register", json={"username": "ALICE", "password": PASSWORD}).status_code == 409


def test_email_cannot_be_shared_between_accounts(anon):
    payload = {"email": "shared@example.com", "password": PASSWORD}
    assert anon.post("/auth/register", json={"username": "one", **payload}).status_code == 201
    assert anon.post("/auth/register", json={"username": "two", **payload}).status_code == 409


def test_email_can_be_added_later_but_not_stolen(client, other_client):
    assert client.put("/auth/me", json={"email": "alice@example.com"}).json()["email"] == "alice@example.com"
    assert other_client.put("/auth/me", json={"email": "ALICE@example.com"}).status_code == 409


def test_password_is_hashed_and_duplicates_rejected(client):
    with engine.connect() as conn:
        stored = conn.execute(text("SELECT password_hash FROM users")).scalar_one()
    assert stored.startswith("$argon2") and PASSWORD not in stored
    assert client.post("/auth/register", json={"username": "alice", "password": PASSWORD}).status_code == 409


def test_weak_password_rejected(anon):
    assert anon.post("/auth/register", json={"username": "alice", "password": "short"}).status_code == 422


def test_bearer_token_is_accepted(client):
    token = client.cookies.get(settings.COOKIE_NAME)
    client.cookies.clear()
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.get("/auth/me", headers={"Authorization": "Bearer forged"}).status_code == 401


def test_login_is_rate_limited(client):
    client.post("/auth/logout")
    bad = {"username": "alice", "password": "wrong-password"}
    codes = [client.post("/auth/login", json=bad).status_code for _ in range(settings.LOGIN_MAX_ATTEMPTS)]
    assert codes == [401] * settings.LOGIN_MAX_ATTEMPTS
    good = {"username": "alice", "password": PASSWORD}
    assert client.post("/auth/login", json=good).status_code == 429


def test_registration_can_be_disabled(anon, monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_REGISTRATION", False)
    assert anon.post("/auth/register", json={"username": "xavier", "password": PASSWORD}).status_code == 403


def test_admin_reset_endpoint_is_gone(client):
    assert client.delete("/admin/reset").status_code in (404, 405)


def test_first_account_adopts_legacy_data(anon):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO companies (id, name) VALUES ('co', 'Legacy')"))
        conn.execute(text("INSERT INTO clients (id, company_id, first_name) VALUES ('cl', 'co', 'Anne')"))
    anon.post("/auth/register", json={"username": "first", "password": PASSWORD})
    assert [c["name"] for c in anon.get("/companies/").json()] == ["Legacy"]
    assert [c["first_name"] for c in anon.get("/clients/").json()] == ["Anne"]


def test_users_are_isolated(client, other_client):
    company = client.post("/companies/", json={"name": "Acme"}).json()
    customer = client.post("/clients/", json={"company_id": company["id"], "first_name": "Alice"}).json()
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "Secret"}).json()

    assert other_client.get("/tasks/").json()["items"] == []
    assert other_client.get("/clients/").json() == []
    assert other_client.get("/companies/").json() == []
    assert other_client.get(f"/tasks/{task['id']}").status_code == 404
    assert other_client.put(f"/tasks/{task['id']}", json={"title": "pwned"}).status_code == 404
    assert other_client.delete(f"/clients/{customer['id']}").status_code == 404
    assert other_client.post(f"/tasks/{task['id']}/comments", json={"content": "x"}).status_code == 404
    # Impossible de rattacher ses propres objets à ceux d'un autre compte
    assert (
        other_client.post("/clients/", json={"company_id": company["id"], "first_name": "X"}).status_code
        == 404
    )
    assert other_client.post("/tasks/", json={"client_id": customer["id"], "title": "X"}).status_code == 404
    # Le même nom d'entreprise reste disponible pour un autre compte
    assert other_client.post("/companies/", json={"name": "Acme"}).status_code == 201


def test_production_refuses_default_secret(monkeypatch):
    import pytest

    from app.config import Settings

    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(ENVIRONMENT="production")
    assert Settings(ENVIRONMENT="production", SECRET_KEY="x" * 40, COOKIE_SECURE=None).cookie_secure is True
