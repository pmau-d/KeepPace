from datetime import timedelta

from app.presence import today
from tests.test_projects import make_project, make_project_task


def test_task_defaults_and_kinds(client):
    project = make_project(client)
    task = make_project_task(client, project["id"])
    assert (task["kind"], task["status"], task["priority"]) == ("TASK", "TODO", "MEDIUM")
    bug = make_project_task(client, project["id"], "Crash au login", kind="BUG", priority="HIGH")
    assert bug["kind"] == "BUG"


def test_filter_by_kind_and_hide_done_by_default(client):
    project = make_project(client)
    make_project_task(client, project["id"], "Tâche")
    bug = make_project_task(client, project["id"], "Bug", kind="BUG")
    make_project_task(client, project["id"], "Idée", kind="IMPROVEMENT")
    done = make_project_task(client, project["id"], "Bug réglé", kind="BUG")
    client.post(f"/project-tasks/{done['id']}/close")

    def titles(**params):
        return sorted(t["title"] for t in client.get("/project-tasks/", params=params).json())

    assert titles(project_id=project["id"], kind="BUG") == ["Bug"]
    assert titles(project_id=project["id"]) == ["Bug", "Idée", "Tâche"]
    assert titles(project_id=project["id"], kind="BUG", show_done=True) == ["Bug", "Bug réglé"]
    assert bug["project_id"] == project["id"]


def test_list_is_ordered_by_due_date_then_priority(client):
    project = make_project(client)
    day = today()
    make_project_task(client, project["id"], "sans date")
    make_project_task(client, project["id"], "tard", due_date=(day + timedelta(days=9)).isoformat())
    make_project_task(
        client, project["id"], "tôt basse", due_date=(day + timedelta(days=1)).isoformat(), priority="LOW"
    )
    make_project_task(
        client, project["id"], "tôt haute", due_date=(day + timedelta(days=1)).isoformat(), priority="HIGH"
    )
    titles = [t["title"] for t in client.get("/project-tasks/").json()]
    assert titles == ["tôt haute", "tôt basse", "tard", "sans date"]


def test_update_close_reopen(client):
    project = make_project(client)
    task = make_project_task(client, project["id"])
    updated = client.put(f"/project-tasks/{task['id']}", json={"kind": "BUG", "status": "IN_PROGRESS"})
    assert (updated.json()["kind"], updated.json()["status"]) == ("BUG", "IN_PROGRESS")
    assert client.post(f"/project-tasks/{task['id']}/close").json()["status"] == "DONE"
    assert client.post(f"/project-tasks/{task['id']}/reopen").json()["status"] == "TODO"


def test_null_is_ignored_for_required_fields(client):
    project = make_project(client)
    task = make_project_task(client, project["id"])
    response = client.put(f"/project-tasks/{task['id']}", json={"title": None, "status": None})
    assert response.status_code == 200
    assert (response.json()["title"], response.json()["status"]) == (task["title"], "TODO")


def test_closing_a_recurring_task_creates_the_next_one_once(client):
    project = make_project(client)
    due = today() + timedelta(days=1)
    task = make_project_task(
        client,
        project["id"],
        "Passer en revue les tickets",
        kind="BUG",
        due_date=due.isoformat(),
        recurrence="WEEKLY",
        recurrence_interval=2,
    )
    client.post(f"/project-tasks/{task['id']}/close")
    # Réouvrir puis refermer ne la duplique pas
    client.post(f"/project-tasks/{task['id']}/reopen")
    client.post(f"/project-tasks/{task['id']}/close")

    open_tasks = client.get("/project-tasks/", params={"project_id": project["id"]}).json()
    assert len(open_tasks) == 1
    follow = open_tasks[0]
    assert follow["due_date"] == (due + timedelta(weeks=2)).isoformat()
    assert (follow["kind"], follow["status"], follow["recurrence_interval"]) == ("BUG", "TODO", 2)


def test_updating_status_to_done_also_spawns_the_next_occurrence(client):
    project = make_project(client)
    task = make_project_task(client, project["id"], recurrence="DAILY")
    client.put(f"/project-tasks/{task['id']}", json={"status": "DONE"})
    assert len(client.get("/project-tasks/", params={"project_id": project["id"]}).json()) == 1


def test_tasks_are_isolated_between_accounts(client, other_client):
    project = make_project(client)
    task = make_project_task(client, project["id"])
    assert other_client.get("/project-tasks/").json() == []
    assert other_client.put(f"/project-tasks/{task['id']}", json={"title": "x"}).status_code == 404
    assert other_client.post(f"/project-tasks/{task['id']}/close").status_code == 404
    assert other_client.delete(f"/project-tasks/{task['id']}").status_code == 404


def test_cannot_add_a_task_to_an_archived_project(client):
    project = make_project(client)
    client.delete(f"/projects/{project['id']}")
    response = client.post("/project-tasks/", json={"project_id": project["id"], "title": "x"})
    assert response.status_code == 404


def test_recurrence_interval_is_validated(client):
    project = make_project(client)
    response = client.post(
        "/project-tasks/",
        json={"project_id": project["id"], "title": "x", "recurrence": "WEEKLY", "recurrence_interval": 0},
    )
    assert response.status_code == 422
