from fastapi.testclient import TestClient

from app.main import app
from app.security import public_limiter
from tests.test_projects import make_project, make_project_task


def publish(api, project):
    response = api.put(f"/projects/{project['id']}", json={"is_public": True})
    assert response.status_code == 200, response.text
    return response.json()


def visitor() -> TestClient:
    """Visiteur sans compte ni cookie."""
    return TestClient(app)


def test_projects_are_private_by_default(client):
    project = make_project(client)
    assert project["is_public"] is False
    with visitor() as web:
        assert web.get("/public/projects/").json() == []
        assert web.get(f"/public/projects/{project['slug']}").status_code == 404


def test_published_project_is_visible_without_logging_in(client):
    project = publish(client, make_project(client, "Site vitrine", description="Refonte du site"))
    with visitor() as web:
        cards = web.get("/public/projects/").json()
        assert cards == [
            {
                "name": "Site vitrine",
                "slug": "site-vitrine",
                "description": "Refonte du site",
                "status": "IDEA",
                "progress": 0,
            }
        ]
        detail = web.get(f"/public/projects/{project['slug']}")
        assert detail.status_code == 200
        assert detail.json()["completed_tasks"] == []


def test_public_pages_never_leak_private_data(client):
    project = publish(client, make_project(client, "Vitrine", description="Public"))
    pid = project["id"]
    make_project_task(client, pid, "SECRET tâche en cours")
    archived = make_project_task(client, pid, "SECRET tâche archivée")
    done_bug = make_project_task(client, pid, "SECRET bug corrigé", kind="BUG")
    done_idea = make_project_task(client, pid, "SECRET retour traité", kind="IMPROVEMENT")
    shown = make_project_task(client, pid, "Page d'accueil livrée")
    for task in (done_bug, done_idea, shown):
        client.post(f"/project-tasks/{task['id']}/close")
    client.delete(f"/project-tasks/{archived['id']}")
    client.post("/companies/", json={"name": "SECRET Client SA"})

    with visitor() as web:
        for path in ("/public/projects/", f"/public/projects/{project['slug']}"):
            text = web.get(path).text
            assert "SECRET" not in text, path
            assert project["id"] not in text, path
        detail = web.get(f"/public/projects/{project['slug']}").json()

    # Seules les tâches terminées (hors bugs et retours) sont montrées, avec une date
    assert [t["title"] for t in detail["completed_tasks"]] == ["Page d'accueil livrée"]
    assert set(detail["completed_tasks"][0]) == {"title", "completed_at"}
    # Et uniquement ces champs, ni identifiant ni compte
    assert set(detail) == {"name", "slug", "description", "status", "progress", "completed_tasks"}


def test_private_archived_or_unknown_projects_answer_404(client):
    project = publish(client, make_project(client, "Alpha"))
    with visitor() as web:
        assert web.get("/public/projects/alpha").status_code == 200
        assert web.get("/public/projects/inconnu").status_code == 404

    client.put(f"/projects/{project['id']}", json={"is_public": False})
    with visitor() as web:
        assert web.get("/public/projects/alpha").status_code == 404
        assert web.get("/public/projects/").json() == []

    publish(client, project)
    client.delete(f"/projects/{project['id']}")
    with visitor() as web:
        assert web.get("/public/projects/alpha").status_code == 404
        assert web.get("/public/projects/").json() == []


def test_public_routes_are_read_only(client):
    project = publish(client, make_project(client))
    with visitor() as web:
        for method in (web.post, web.put, web.delete):
            assert method(f"/public/projects/{project['slug']}").status_code in (404, 405)


def test_public_address_is_unique_among_public_projects(client, other_client):
    mine = make_project(client, "Alpha")
    theirs = make_project(other_client, "Alpha")
    assert mine["slug"] == theirs["slug"] == "alpha"
    publish(client, mine)
    # Le second compte ne peut pas prendre la même adresse publique
    response = other_client.put(f"/projects/{theirs['id']}", json={"is_public": True})
    assert response.status_code == 409
    # Une fois la première dépubliée, elle se libère
    client.put(f"/projects/{mine['id']}", json={"is_public": False})
    assert other_client.put(f"/projects/{theirs['id']}", json={"is_public": True}).status_code == 200


def test_restoring_a_project_whose_address_was_taken_makes_it_private_again(client, other_client):
    mine = publish(client, make_project(client, "Alpha"))
    client.delete(f"/projects/{mine['id']}")
    publish(other_client, make_project(other_client, "Alpha"))
    restored = client.post(f"/projects/{mine['id']}/restore").json()
    assert restored["is_public"] is False


def test_cannot_publish_someone_elses_project(client, other_client):
    project = make_project(client)
    assert other_client.put(f"/projects/{project['id']}", json={"is_public": True}).status_code == 404


def test_public_routes_are_rate_limited(client, monkeypatch):
    publish(client, make_project(client))
    monkeypatch.setattr(public_limiter, "max_attempts", 3)
    with visitor() as web:
        codes = [web.get("/public/projects/").status_code for _ in range(5)]
    assert codes == [200, 200, 200, 429, 429]


def test_public_responses_can_be_cached_briefly(client):
    project = publish(client, make_project(client))
    with visitor() as web:
        assert "max-age" in web.get("/public/projects/").headers["cache-control"]
        assert "max-age" in web.get(f"/public/projects/{project['slug']}").headers["cache-control"]


def test_showcase_answers_even_when_no_account_exists(anon):
    # Sans compte du tout, la vitrine répond (liste vide) au lieu de 401.
    assert anon.get("/public/projects/").json() == []
