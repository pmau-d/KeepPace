def make_project(api, name="Site vitrine", **extra):
    response = api.post("/projects/", json={"name": name, **extra})
    assert response.status_code == 201, response.text
    return response.json()


def make_project_task(api, project_id, title="Corriger", **extra):
    response = api.post("/project-tasks/", json={"project_id": project_id, "title": title, **extra})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_project_has_defaults_and_a_clean_slug(client):
    project = make_project(client, "Mon Été à Zürich !")
    assert project["slug"] == "mon-ete-a-zurich"
    assert project["status"] == "IDEA"
    assert (project["tasks_total"], project["tasks_done"], project["progress"]) == (0, 0, 0)


def test_slug_is_unique_per_account(client, other_client):
    assert make_project(client, "Alpha")["slug"] == "alpha"
    assert make_project(client, "Alpha")["slug"] == "alpha-2"
    assert make_project(client, "Alpha")["slug"] == "alpha-3"
    # Un autre compte peut réutiliser le même nom
    assert make_project(other_client, "Alpha")["slug"] == "alpha"


def test_slug_survives_a_rename_so_links_stay_valid(client):
    project = make_project(client, "Alpha")
    renamed = client.put(f"/projects/{project['id']}", json={"name": "Beta"}).json()
    assert (renamed["name"], renamed["slug"]) == ("Beta", "alpha")


def test_update_project(client):
    project = make_project(client)
    updated = client.put(
        f"/projects/{project['id']}", json={"status": "ACTIVE", "description": "Refonte"}
    ).json()
    assert (updated["status"], updated["description"]) == ("ACTIVE", "Refonte")


def test_projects_are_isolated_between_accounts(client, other_client):
    project = make_project(client)
    assert other_client.get("/projects/").json() == []
    assert other_client.get(f"/projects/{project['id']}").status_code == 404
    assert other_client.put(f"/projects/{project['id']}", json={"name": "x"}).status_code == 404
    assert other_client.delete(f"/projects/{project['id']}").status_code == 404
    # Et impossible de lui rattacher une tâche
    response = other_client.post("/project-tasks/", json={"project_id": project["id"], "title": "x"})
    assert response.status_code == 404


def test_progress_counts_active_tasks_only(client):
    project = make_project(client)
    first = make_project_task(client, project["id"], "A")
    make_project_task(client, project["id"], "B")
    archived = make_project_task(client, project["id"], "C")
    client.post(f"/project-tasks/{first['id']}/close")
    client.delete(f"/project-tasks/{archived['id']}")

    read = client.get(f"/projects/{project['id']}").json()
    assert (read["tasks_total"], read["tasks_done"], read["progress"]) == (2, 1, 50)


def test_archive_cascades_and_restore_only_brings_back_what_was_archived_with_it(client):
    project = make_project(client)
    kept = make_project_task(client, project["id"], "Gardée")
    already = make_project_task(client, project["id"], "Déjà archivée")
    client.delete(f"/project-tasks/{already['id']}")

    assert client.delete(f"/projects/{project['id']}").status_code == 204
    assert client.get("/projects/").json() == []
    assert [p["id"] for p in client.get("/projects/", params={"archived": True}).json()] == [project["id"]]
    assert client.get("/project-tasks/", params={"project_id": project["id"]}).json() == []

    restored = client.post(f"/projects/{project['id']}/restore")
    assert restored.status_code == 200
    titles = [t["title"] for t in client.get("/project-tasks/", params={"project_id": project["id"]}).json()]
    assert titles == [kept["title"]]


def test_project_name_is_required(client):
    assert client.post("/projects/", json={"name": "   "}).status_code == 422
