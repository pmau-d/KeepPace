from datetime import date, timedelta

import pytest

from app.enums import Recurrence
from app.presence import today
from app.recurrence import describe, next_occurrence
from tests.test_api import make_client

TODAY = date(2026, 10, 1)


@pytest.mark.parametrize(
    ("due", "recurrence", "interval", "expected"),
    [
        (date(2026, 10, 1), Recurrence.DAILY, 1, date(2026, 10, 2)),
        (date(2026, 10, 1), Recurrence.WEEKLY, 2, date(2026, 10, 15)),
        (date(2026, 10, 31), Recurrence.MONTHLY, 1, date(2026, 11, 30)),
        (date(2028, 2, 29), Recurrence.YEARLY, 1, date(2029, 2, 28)),
        # Terminée en retard : on saute les occurrences passées en gardant le rythme
        (date(2026, 9, 3), Recurrence.WEEKLY, 1, date(2026, 10, 8)),
        # Sans échéance : à partir d'aujourd'hui
        (None, Recurrence.MONTHLY, 1, date(2026, 11, 1)),
    ],
)
def test_next_occurrence(due, recurrence, interval, expected):
    assert next_occurrence(due, recurrence, interval, TODAY) == expected


def test_monthly_rhythm_does_not_drift_after_a_short_month():
    # 31 janv. terminé fin mars : 28 févr. est passé, la suivante est le 31 mars, pas le 28.
    assert next_occurrence(date(2026, 1, 31), Recurrence.MONTHLY, 1, date(2026, 3, 1)) == date(2026, 3, 31)


def test_describe():
    assert describe(Recurrence.WEEKLY, 1) == "chaque semaine"
    assert describe(Recurrence.DAILY, 3) == "tous les 3 jours"
    assert describe(Recurrence.YEARLY, 1) == "chaque année"
    assert describe(Recurrence.WEEKLY, 2) == "toutes les 2 semaines"


def test_closing_a_recurring_task_creates_the_next_one(client):
    customer = make_client(client)
    due = today() + timedelta(days=2)
    task = client.post(
        "/tasks/",
        json={
            "client_id": customer["id"],
            "title": "Point hebdo",
            "priority": "HIGH",
            "due_date": due.isoformat(),
            "recurrence": "WEEKLY",
        },
    ).json()
    assert task["recurrence"] == "WEEKLY" and task["recurrence_interval"] == 1

    client.post(f"/tasks/{task['id']}/close")

    open_tasks = client.get("/tasks/").json()["items"]
    assert len(open_tasks) == 1
    follow = open_tasks[0]
    assert follow["id"] != task["id"]
    assert follow["title"] == "Point hebdo" and follow["priority"] == "HIGH"
    assert follow["due_date"] == (due + timedelta(weeks=1)).isoformat()
    assert follow["recurrence"] == "WEEKLY"

    logs = client.get(f"/tasks/{task['id']}/logs").json()
    assert logs[-1]["field_changed"] == "next_occurrence"
    assert logs[-1]["new_value"] == follow["due_date"]
    created = client.get(f"/tasks/{follow['id']}/logs").json()[0]
    assert created["comment"] == "Tâche créée (récurrence : chaque semaine)"

    # Réouvrir puis refermer (ici via PUT) ne crée pas une seconde occurrence suivante
    client.post(f"/tasks/{task['id']}/reopen")
    client.put(f"/tasks/{task['id']}", json={"status": "DONE"})
    assert [t["id"] for t in client.get("/tasks/").json()["items"]] == [follow["id"]]


def test_one_off_task_creates_nothing(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "Unique"}).json()
    client.post(f"/tasks/{task['id']}/close")
    assert client.get("/tasks/").json()["items"] == []


def test_recurrence_is_editable_and_logged(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "Rapport"}).json()
    updated = client.put(
        f"/tasks/{task['id']}", json={"recurrence": "MONTHLY", "recurrence_interval": 3}
    ).json()
    assert (updated["recurrence"], updated["recurrence_interval"]) == ("MONTHLY", 3)
    fields = [log["field_changed"] for log in client.get(f"/tasks/{task['id']}/logs").json()]
    assert {"recurrence", "recurrence_interval"} <= set(fields)
    assert client.put(f"/tasks/{task['id']}", json={"recurrence": "HOURLY"}).status_code == 422
