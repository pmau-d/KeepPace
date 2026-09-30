import pytest

from app.database import SessionLocal
from scripts.seed_demo import DEMO_EMAIL, DEMO_PASSWORD, seed


def test_demo_seed_creates_a_usable_account(anon):
    with SessionLocal() as db:
        seed(db)
    assert anon.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}).status_code == 200
    assert anon.get("/tasks/").json()["total"] == 8  # la tâche terminée est masquée par défaut
    reasons = {t["follow_up_reason"] for t in anon.get("/tasks/follow-up").json()}
    assert {"OVERDUE", "DUE_TODAY", "CLIENT_LEAVING", "CLIENT_BACK", "WAITING"} <= reasons

    with SessionLocal() as db, pytest.raises(SystemExit):
        seed(db)  # jamais deux fois
