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
