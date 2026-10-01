from datetime import timedelta

from app.presence import today
from app.types import utcnow


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

    assert client.get("/tasks/").json()["items"] == []
    assert len(client.get("/tasks/", params={"show_done": True}).json()["items"]) == 1


def test_presence_status(client):
    on = today()

    def d(days):
        return (on + timedelta(days=days)).isoformat()

    cases = [
        ({}, "PRESENT"),
        ({"absence_end_date": d(10)}, "ABSENT"),
        ({"absence_end_date": d(3)}, "SOON_BACK"),
        ({"absence_end_date": d(0)}, "SOON_BACK"),
        ({"absence_end_date": d(-1)}, "RECENTLY_BACK"),
        ({"absence_end_date": d(-5)}, "RECENTLY_BACK"),
        ({"absence_end_date": d(-6)}, "PRESENT"),
        # Avec une date de début
        ({"absence_start_date": d(2), "absence_end_date": d(20)}, "LEAVING_SOON"),
        ({"absence_start_date": d(10), "absence_end_date": d(20)}, "PRESENT"),
        ({"absence_start_date": d(-2), "absence_end_date": d(20)}, "ABSENT"),
        ({"absence_start_date": d(-2)}, "ABSENT"),  # retour non daté
    ]
    for index, (period, expected) in enumerate(cases):
        customer = make_client(client, company=f"C{index}", **period)
        assert customer["presence_status"] == expected, (period, customer["presence_status"])
        client.post("/tasks/", json={"client_id": customer["id"], "title": f"t{index}"})

    # Le filtre SQL et le statut renvoyé viennent de la même règle
    for expected in {e for _, e in cases}:
        filtered = client.get("/tasks/", params={"presence_status": expected}).json()["items"]
        assert filtered and {t["client"]["presence_status"] for t in filtered} == {expected}


def test_absence_end_must_follow_start(client):
    company_id = client.post("/companies/", json={"name": "Acme"}).json()["id"]
    bad = {
        "company_id": company_id,
        "first_name": "A",
        "absence_start_date": "2026-10-10",
        "absence_end_date": "2026-10-01",
    }
    assert client.post("/clients/", json=bad).status_code == 422
    ok = make_client(client, company="Globex", absence_start_date="2026-10-10")
    assert client.put(f"/clients/{ok['id']}", json={"absence_end_date": "2026-10-01"}).status_code == 422


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

    assert client.get("/tasks/").json()["items"] == []
    assert client.get(f"/tasks/{task['id']}").status_code == 404
    assert [t["id"] for t in client.get("/tasks/", params={"archived": True}).json()["items"]] == [task["id"]]
    logs = client.get(f"/tasks/{task['id']}/logs").json()
    assert logs[-1]["field_changed"] == "archived"

    restored = client.post(f"/tasks/{task['id']}/restore")
    assert restored.status_code == 200
    assert [t["id"] for t in client.get("/tasks/").json()["items"]] == [task["id"]]


def test_archiving_a_company_cascades_and_restores_only_what_it_archived(client):
    alice = make_client(client, company="Acme", first_name="Alice")
    bob = client.post("/clients/", json={"company_id": alice["company_id"], "first_name": "Bob"}).json()
    kept = client.post("/tasks/", json={"client_id": alice["id"], "title": "Garder"}).json()
    old = client.post("/tasks/", json={"client_id": alice["id"], "title": "Déjà archivée"}).json()
    client.delete(f"/tasks/{old['id']}")
    client.delete(f"/clients/{bob['id']}")

    assert client.delete(f"/companies/{alice['company_id']}").status_code == 204
    assert client.get("/clients/").json() == []
    assert client.get("/tasks/").json()["items"] == []
    assert client.post(f"/clients/{alice['id']}/restore").status_code == 409

    assert client.post(f"/companies/{alice['company_id']}/restore").status_code == 200
    assert [c["first_name"] for c in client.get("/clients/").json()] == ["Alice"]
    assert [t["id"] for t in client.get("/tasks/").json()["items"]] == [kept["id"]]


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


def test_list_is_paginated_and_light(client):
    customer = make_client(client)
    for i in range(5):
        client.post(
            "/tasks/", json={"client_id": customer["id"], "title": f"t{i}", "due_date": f"2026-10-0{i + 1}"}
        )
    page = client.get("/tasks/", params={"limit": 2, "offset": 2}).json()
    assert (page["total"], page["limit"], page["offset"]) == (5, 2, 2)
    assert [t["title"] for t in page["items"]] == ["t2", "t3"]
    assert "comments" not in page["items"][0] and "logs" not in page["items"][0]
    assert client.get("/tasks/", params={"limit": 500}).status_code == 422


def test_detail_includes_comments_and_list_counts_them(client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "x"}).json()
    client.post(f"/tasks/{task['id']}/comments", json={"content": "Premier"})
    client.post(f"/tasks/{task['id']}/comments", json={"content": "Second"})
    assert client.get("/tasks/").json()["items"][0]["comments_count"] == 2
    assert [c["content"] for c in client.get(f"/tasks/{task['id']}").json()["comments"]] == [
        "Premier",
        "Second",
    ]


def test_search_covers_title_description_and_comments(client):
    customer = make_client(client)
    by_title = client.post("/tasks/", json={"client_id": customer["id"], "title": "Contrat Acme"}).json()
    by_desc = client.post(
        "/tasks/", json={"client_id": customer["id"], "title": "Autre", "description": "revoir le CONTRAT"}
    ).json()
    by_comment = client.post("/tasks/", json={"client_id": customer["id"], "title": "Encore"}).json()
    client.post(f"/tasks/{by_comment['id']}/comments", json={"content": "contrat signé ?"})
    client.post("/tasks/", json={"client_id": customer["id"], "title": "Sans rapport"})

    found = {t["id"] for t in client.get("/tasks/", params={"search": "contrat"}).json()["items"]}
    assert found == {by_title["id"], by_desc["id"], by_comment["id"]}
    # Les jokers SQL saisis par l'utilisateur sont pris littéralement
    assert client.get("/tasks/", params={"search": "%"}).json()["total"] == 0


def test_follow_up_lists_what_to_chase_today_in_order(client):
    on = today()

    def d(days):
        return (on + timedelta(days=days)).isoformat()

    present = make_client(client, company="P", first_name="Paul")
    back = make_client(client, company="B", first_name="Rita", absence_end_date=d(-2))
    leaving = make_client(client, company="L", first_name="Léo", absence_start_date=d(1))
    away = make_client(client, company="A", first_name="Ana", absence_end_date=d(10))

    def task(customer, title, **extra):
        return client.post("/tasks/", json={"client_id": customer["id"], "title": title, **extra}).json()

    task(present, "En retard", due_date=d(-1))
    task(present, "Aujourd'hui", due_date=d(0))
    task(leaving, "Avant son départ")
    task(back, "Depuis son retour", due_date=d(30))
    task(away, "Client absent", due_date=d(-3))  # injoignable : exclu
    task(present, "Plus tard", due_date=d(5))  # rien d'urgent : exclu
    done = task(present, "Déjà faite", due_date=d(-1))
    client.post(f"/tasks/{done['id']}/close")

    items = client.get("/tasks/follow-up").json()
    assert [(t["title"], t["follow_up_reason"]) for t in items] == [
        ("En retard", "OVERDUE"),
        ("Aujourd'hui", "DUE_TODAY"),
        ("Avant son départ", "CLIENT_LEAVING"),
        ("Depuis son retour", "CLIENT_BACK"),
    ]


def test_csv_export(client):
    customer = make_client(client, company="Acme", first_name="Alice", last_name="Martin")
    client.post(
        "/tasks/",
        json={
            "client_id": customer["id"],
            "title": "=HYPERLINK(1)",
            "priority": "HIGH",
            "due_date": "2026-10-15",
        },
    )
    client.post("/tasks/", json={"client_id": customer["id"], "title": "Autre"})

    response = client.get("/tasks/export.csv", params={"search": "HYPERLINK"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    lines = response.content.decode("utf-8-sig").splitlines()
    assert lines[0].startswith("Titre;Client;Entreprise;Statut")
    assert len(lines) == 2
    # Les formules sont neutralisées (injection CSV)
    assert lines[1].startswith("'=HYPERLINK(1);Alice Martin;Acme;À faire;;Haute;15/10/2026;Présent;0;")


def test_follow_up_includes_stale_waiting_tasks(client):
    from sqlalchemy import bindparam, text

    from app.database import engine
    from app.types import UTCDateTime

    customer = make_client(client)
    stale = client.post(
        "/tasks/", json={"client_id": customer["id"], "title": "Relance", "status": "BLOCKED"}
    ).json()
    client.post("/tasks/", json={"client_id": customer["id"], "title": "Récente", "status": "BLOCKED"})
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tasks SET updated_at = :at WHERE id = :id").bindparams(
                bindparam("at", type_=UTCDateTime)
            ),
            {"at": utcnow() - timedelta(days=4), "id": stale["id"]},
        )
    items = client.get("/tasks/follow-up").json()
    assert [(t["title"], t["follow_up_reason"]) for t in items] == [("Relance", "WAITING")]


def test_health(anon):
    assert anon.get("/health").json() == {"status": "ok"}


def test_clients_count_their_open_tasks(client):
    customer = make_client(client)
    other = make_client(client, company="Globex", first_name="Bob")
    ids = [
        client.post("/tasks/", json={"client_id": customer["id"], "title": f"t{i}"}).json()["id"]
        for i in range(3)
    ]
    client.post(f"/tasks/{ids[0]}/close")
    client.delete(f"/tasks/{ids[1]}")

    counts = {c["id"]: c["open_tasks_count"] for c in client.get("/clients/").json()}
    assert counts == {customer["id"]: 1, other["id"]: 0}


def test_snooze_postpones_the_due_date_and_logs_it(client):
    customer = make_client(client)
    task = client.post(
        "/tasks/", json={"client_id": customer["id"], "title": "Relancer", "status": "BLOCKED"}
    ).json()

    response = client.post(f"/tasks/{task['id']}/snooze", json={"days": 3, "comment": "absent ce matin"})
    assert response.status_code == 200
    assert response.json()["due_date"] == (today() + timedelta(days=3)).isoformat()
    log = client.get(f"/tasks/{task['id']}/logs").json()[-1]
    assert log["field_changed"] == "due_date"
    assert log["old_value"] is None
    assert log["comment"] == "Relance reportée de 3 jours — absent ce matin"

    assert client.post(f"/tasks/{task['id']}/snooze", json={"days": 0}).status_code == 422
    client.post(f"/tasks/{task['id']}/close")
    assert client.post(f"/tasks/{task['id']}/snooze", json={"days": 1}).status_code == 409


def test_snooze_is_scoped_to_the_owner(client, other_client):
    customer = make_client(client)
    task = client.post("/tasks/", json={"client_id": customer["id"], "title": "x"}).json()
    assert other_client.post(f"/tasks/{task['id']}/snooze", json={"days": 1}).status_code == 404
