from datetime import date, timedelta


def make_client(api, company="Acme", first_name="Alice", **extra):
    company_id = api.post("/companies/", json={"name": company}).json()["id"]
    payload = {"company_id": company_id, "first_name": first_name, **extra}
    response = api.post("/clients/", json=payload)
    assert response.status_code == 201
    return response.json()


def test_root(client):
    assert client.get("/").status_code == 200


def test_company_name_is_unique(client):
    assert client.post("/companies/", json={"name": "Acme"}).status_code == 201
    assert client.post("/companies/", json={"name": "Acme"}).status_code == 400


def test_task_lifecycle_is_logged(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "Relancer"}).json()
    assert task["status"] == "TODO"

    client.put(f"/tasks/{task['id']}", json={"status": "IN_PROGRESS", "comment": "démarré"})
    client.post(f"/tasks/{task['id']}/close")

    logs = client.get(f"/tasks/{task['id']}/logs").json()
    assert [log["new_value"] for log in logs] == ["TODO", "IN_PROGRESS", "DONE"]
    assert logs[1]["comment"] == "démarré"

    assert client.get("/tasks/").json() == []
    assert len(client.get("/tasks/", params={"show_done": True}).json()) == 1


def test_presence_status(client):
    today = date.today()
    cases = {
        None: "PRESENT",
        today + timedelta(days=10): "ABSENT",
        today + timedelta(days=2): "SOON_BACK",
        today - timedelta(days=2): "RECENTLY_BACK",
        today - timedelta(days=30): "PRESENT",
    }
    for index, (end, expected) in enumerate(cases.items()):
        extra = {"absence_end_date": end.isoformat()} if end else {}
        customer = make_client(client, company=f"C{index}", **extra)
        assert customer["presence_status"] == expected
        client.post("/tasks/", json={"client_id": customer["id"], "title": f"t{index}"})
        filtered = client.get("/tasks/", params={"presence_status": expected}).json()
        assert customer["id"] in {t["client"]["id"] for t in filtered}


def test_comments(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "Relancer"}).json()
    comment = client.post(f"/tasks/{task['id']}/comments", json={"content": "Appelé"}).json()
    assert client.get(f"/tasks/{task['id']}/comments").json()[0]["content"] == "Appelé"
    assert client.delete(f"/tasks/{task['id']}/comments/{comment['id']}").status_code == 204


def test_unknown_status_and_priority_are_rejected(client):
    customer = make_client(client)
    base = {"client_id": customer["id"], "title": "x"}
    assert client.post("/tasks/", json={**base, "status": "WHATEVER"}).status_code == 422
    assert client.post("/tasks/", json={**base, "priority": "URGENT"}).status_code == 422


def test_timestamps_are_timezone_aware(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "x"}).json()
    assert task["created_at"].endswith(("Z", "+00:00"))


def test_deleting_a_task_archives_it_and_keeps_history(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "Relancer"}).json()
    assert client.delete(f"/tasks/{task['id']}").status_code == 204

    assert client.get("/tasks/").json() == []
    assert client.get(f"/tasks/{task['id']}").status_code == 404
    assert [t["id"] for t in client.get("/tasks/", params={"archived": True}).json()] == [task["id"]]
    logs = client.get(f"/tasks/{task['id']}/logs").json()
    assert logs[-1]["field_changed"] == "archived"

    restored = client.post(f"/tasks/{task['id']}/restore")
    assert restored.status_code == 200
    assert [t["id"] for t in client.get("/tasks/").json()] == [task["id"]]


def test_archiving_a_company_cascades_and_restores_only_what_it_archived(client):
    alice = make_client(client, company="Acme", first_name="Alice")
    bob = client.post("/clients/", json={"company_id": alice["company_id"], "first_name": "Bob"}).json()
    kept = client.post("/tasks/", json={"client_id": alice["id"], "title": "Garder"}).json()
    old = client.post("/tasks/", json={"client_id": alice["id"], "title": "Déjà archivée"}).json()
    client.delete(f"/tasks/{old['id']}")
    client.delete(f"/clients/{bob['id']}")

    assert client.delete(f"/companies/{alice['company_id']}").status_code == 204
    assert client.get("/clients/").json() == []
    assert client.get("/tasks/").json() == []
    assert client.post(f"/clients/{alice['id']}/restore").status_code == 409

    assert client.post(f"/companies/{alice['company_id']}/restore").status_code == 200
    assert [c["first_name"] for c in client.get("/clients/").json()] == ["Alice"]
    assert [t["id"] for t in client.get("/tasks/").json()] == [kept["id"]]


def test_archived_company_name_can_be_reused(client):
    company = client.post("/companies/", json={"name": "Acme"}).json()
    client.delete(f"/companies/{company['id']}")
    assert client.post("/companies/", json={"name": "Acme"}).status_code == 201
    assert client.post(f"/companies/{company['id']}/restore").status_code == 409


def test_client_change_is_logged_with_readable_names(client):
    alice = make_client(client, company="Acme", first_name="Alice", last_name="Martin")
    bob = make_client(client, company="Globex", first_name="Bob")
    task = client.post("/tasks/", json={"client_id": alice["id"], "title": "x"}).json()
    client.put(f"/tasks/{task['id']}", json={"client_id": bob["id"]})
    log = client.get(f"/tasks/{task['id']}/logs").json()[-1]
    assert (log["old_label"], log["new_label"]) == ("Alice Martin · Acme", "Bob · Globex")


def test_deleted_comment_is_kept_in_history(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "x"}).json()
    comment = client.post(f"/tasks/{task['id']}/comments", json={"content": "Appel du 12"}).json()
    client.delete(f"/tasks/{task['id']}/comments/{comment['id']}")
    log = client.get(f"/tasks/{task['id']}/logs").json()[-1]
    assert (log["field_changed"], log["old_value"]) == ("comment", "Appel du 12")
