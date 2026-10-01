from datetime import timedelta
from unittest.mock import patch

from app.config import settings
from app.presence import today
from tests.test_api import make_client


def _d(days: int) -> str:
    return (today() + timedelta(days=days)).isoformat()


def test_digest_lists_follow_ups_departures_and_returns(client):
    ines = make_client(client, first_name="Inès", absence_start_date=_d(2), absence_end_date=_d(9))
    hugo = make_client(
        client, company="Globex", first_name="Hugo", absence_start_date=_d(-6), absence_end_date=_d(1)
    )
    camille = make_client(client, company="Initech", first_name="Camille")
    client.post("/tasks/", json={"client_id": camille["id"], "title": "Relancer", "due_date": _d(-1)})

    digest = client.get("/digest/").json()
    assert digest["follow_up_total"] == 1
    assert digest["counts"]["OVERDUE"] == 1
    assert [c["id"] for c in digest["leaving"]] == [ines["id"]]
    assert digest["leaving"][0]["on"] == _d(2)
    assert [c["id"] for c in digest["returning"]] == [hugo["id"]]
    assert digest["returning"][0]["on"] == _d(2)
    assert digest["email_available"] is False


def test_opt_in_is_saved_on_the_account(client):
    assert client.get("/auth/me").json()["digest_opt_in"] is False
    assert client.put("/auth/me", json={"digest_opt_in": True}).json()["digest_opt_in"] is True
    assert client.get("/auth/me").json()["digest_opt_in"] is True


def test_send_now_requires_email_configuration(client):
    assert client.post("/digest/send").status_code == 409


def test_send_now_sends_text_and_html(client, monkeypatch):
    monkeypatch.setattr(settings, "DIGEST_ENABLED", True)
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.com")
    customer = make_client(client, first_name="Camille")
    client.post("/tasks/", json={"client_id": customer["id"], "title": "Devis <urgent>", "due_date": _d(0)})
    with patch("app.routers.digest.send_email") as send:
        response = client.post("/digest/send")
    assert response.status_code == 202
    message = send.call_args.args[0]
    assert message["To"] == "alice@example.com"
    assert message["Subject"] == "KeepPace · 1 relance aujourd'hui"
    text = message.get_body(("plain",)).get_content()
    html = message.get_body(("html",)).get_content()
    assert "Devis <urgent> — Camille (Échéance aujourd'hui)" in text
    assert "Devis &lt;urgent&gt;" in html


def test_daily_sending_only_to_opted_in_accounts_with_news(client, other_client):
    from app.database import SessionLocal
    from app.digest import send_all_digests

    customer = make_client(client)
    client.post("/tasks/", json={"client_id": customer["id"], "title": "x", "due_date": _d(-2)})
    client.put("/auth/me", json={"digest_opt_in": True})
    other_client.put("/auth/me", json={"digest_opt_in": True})  # rien à signaler : pas d'email

    with patch("app.digest.send_email") as send, SessionLocal() as db:
        assert send_all_digests(db) == 1
    assert send.call_args.args[0]["To"] == "alice@example.com"
