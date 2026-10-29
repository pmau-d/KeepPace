from datetime import timedelta

import pytest

from app.presence import today
from tests.test_api import make_client
from tests.test_projects import make_project, make_project_task


def make_task(api, kind, **extra):
    """Une tâche client ou de projet, et le préfixe de ses routes de checklist."""
    if kind == "client":
        customer = make_client(api)
        task = api.post("/tasks/", json={"client_id": customer["id"], "title": "Revue", **extra}).json()
        return task, f"/tasks/{task['id']}"
    project = make_project(api)
    task = make_project_task(api, project["id"], "Revue", **extra)
    return task, f"/project-tasks/{task['id']}"


def read(api, kind, task_id):
    return api.get(f"/tasks/{task_id}" if kind == "client" else f"/project-tasks/{task_id}").json()


def add(api, base, label):
    response = api.post(f"{base}/checklist", json={"label": label})
    assert response.status_code == 201, response.text
    return response.json()


KINDS = pytest.mark.parametrize("kind", ["client", "project"])


@KINDS
def test_add_check_rename_and_delete_items(client, kind):
    task, base = make_task(client, kind)
    first = add(client, base, "Relire les tickets ouverts")
    second = add(client, base, "Répondre aux retours")
    assert (first["position"], second["position"], first["done"]) == (0, 1, False)

    checked = client.put(f"{base}/checklist/{first['id']}", json={"done": True})
    assert checked.json()["done"] is True
    renamed = client.put(f"{base}/checklist/{second['id']}", json={"label": "Répondre aux clients"})
    assert renamed.json()["label"] == "Répondre aux clients"

    items = read(client, kind, task["id"])["checklist"]
    assert [(i["label"], i["done"]) for i in items] == [
        ("Relire les tickets ouverts", True),
        ("Répondre aux clients", False),
    ]
    assert client.delete(f"{base}/checklist/{first['id']}").status_code == 204
    assert [i["label"] for i in read(client, kind, task["id"])["checklist"]] == ["Répondre aux clients"]


@KINDS
def test_label_is_trimmed_and_required(client, kind):
    _, base = make_task(client, kind)
    assert add(client, base, "  Vérifier  ")["label"] == "Vérifier"
    assert client.post(f"{base}/checklist", json={"label": "   "}).status_code == 422
    assert client.post(f"{base}/checklist", json={"label": "x" * 201}).status_code == 422


@KINDS
def test_unknown_item_is_404(client, kind):
    _, base = make_task(client, kind)
    assert client.put(f"{base}/checklist/nope", json={"done": True}).status_code == 404
    assert client.delete(f"{base}/checklist/nope").status_code == 404


@KINDS
def test_items_are_isolated_between_accounts(client, other_client, kind):
    task, base = make_task(client, kind)
    item = add(client, base, "Privé")
    assert other_client.post(f"{base}/checklist", json={"label": "x"}).status_code == 404
    assert other_client.put(f"{base}/checklist/{item['id']}", json={"done": True}).status_code == 404
    assert other_client.delete(f"{base}/checklist/{item['id']}").status_code == 404
    assert read(client, kind, task["id"])["checklist"][0]["done"] is False


def test_an_item_cannot_be_reached_through_another_task(client):
    _, base_a = make_task(client, "client")
    _, base_b = make_task(client, "project")
    item = add(client, base_a, "A")
    # Ni via une autre tâche, ni via l'autre type de tâche
    assert client.put(f"{base_b}/checklist/{item['id']}", json={"done": True}).status_code == 404


def test_list_shows_progress_counts_for_client_tasks(client):
    _, base = make_task(client, "client")
    for label in ("a", "b", "c"):
        item = add(client, base, label)
    client.put(f"{base}/checklist/{item['id']}", json={"done": True})
    listed = client.get("/tasks/").json()["items"][0]
    assert (listed["checklist_done"], listed["checklist_total"]) == (1, 3)


def test_client_task_checklist_changes_are_in_the_history(client):
    _, base = make_task(client, "client")
    item = add(client, base, "Vérifier")
    client.put(f"{base}/checklist/{item['id']}", json={"done": True})
    client.put(f"{base}/checklist/{item['id']}", json={"done": False})
    client.put(f"{base}/checklist/{item['id']}", json={"label": "Revérifier"})
    client.delete(f"{base}/checklist/{item['id']}")
    logs = [log for log in client.get(f"{base}/logs").json() if log["field_changed"] == "checklist"]
    assert [log["comment"] for log in logs] == [
        "Case ajoutée : « Vérifier »",
        "Case cochée : « Vérifier »",
        "Case décochée : « Vérifier »",
        "Case renommée : « Vérifier » → « Revérifier »",
        "Case supprimée : « Revérifier »",
    ]


def test_unchanged_check_state_is_not_logged_twice(client):
    _, base = make_task(client, "client")
    item = add(client, base, "x")
    client.put(f"{base}/checklist/{item['id']}", json={"done": False})
    logs = [log for log in client.get(f"{base}/logs").json() if log["field_changed"] == "checklist"]
    assert len(logs) == 1  # seulement l'ajout


def test_recurring_client_task_copies_an_unchecked_checklist(client):
    due = (today() + timedelta(days=1)).isoformat()
    task, base = make_task(client, "client", due_date=due, recurrence="WEEKLY", recurrence_interval=2)
    for label in ("Relire les tickets", "Trier les bugs"):
        item = add(client, base, label)
        client.put(f"{base}/checklist/{item['id']}", json={"done": True})

    client.post(f"{base}/close")
    tasks = client.get("/tasks/", params={"show_done": True}).json()["items"]
    follow = next(t for t in tasks if t["id"] != task["id"])
    copied = read(client, "client", follow["id"])["checklist"]
    assert [(i["label"], i["done"]) for i in copied] == [
        ("Relire les tickets", False),
        ("Trier les bugs", False),
    ]
    # L'occurrence terminée garde ses cases cochées : trace de ce qui a été vérifié
    assert all(i["done"] for i in read(client, "client", task["id"])["checklist"])


def test_recurring_project_task_copies_an_unchecked_checklist(client):
    task, base = make_task(client, "project", recurrence="WEEKLY")
    item = add(client, base, "Relire les tickets")
    client.put(f"{base}/checklist/{item['id']}", json={"done": True})
    client.post(f"{base}/close")

    follow = client.get("/project-tasks/").json()[0]
    assert follow["id"] != task["id"]
    assert [(i["label"], i["done"]) for i in follow["checklist"]] == [("Relire les tickets", False)]
    assert all(i["done"] for i in read(client, "project", task["id"])["checklist"])
    # Les deux checklists sont indépendantes
    client.put(f"/project-tasks/{follow['id']}/checklist/{follow['checklist'][0]['id']}", json={"done": True})
    assert all(i["done"] for i in read(client, "project", task["id"])["checklist"])


def test_closing_a_task_does_not_require_a_complete_checklist(client):
    # « Terminer ? » est une suggestion de l'interface : l'API laisse le choix.
    _, base = make_task(client, "client")
    add(client, base, "Pas fait")
    assert client.post(f"{base}/close").json()["status"] == "DONE"
