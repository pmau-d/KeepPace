"""Vitrine publique : la seule partie de l'API accessible sans connexion.

Lecture seule, et uniquement les champs des schémas `Public*` (voir app/schemas.py).
Un projet privé, archivé ou inconnu répond 404 : rien ne révèle qu'il existe.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.enums import TaskKind, TaskStatus
from app.security import public_limiter

# Ce que la vitrine montre, au plus, des tâches terminées.
COMPLETED_TASKS_LIMIT = 50
CACHE_CONTROL = "public, max-age=60"


def _rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "?"
    if public_limiter.is_blocked(key):
        raise HTTPException(status_code=429, detail="Trop de requêtes. Réessayez dans un instant.")
    public_limiter.record_failure(key)


router = APIRouter(prefix="/public/projects", tags=["public"], dependencies=[Depends(_rate_limit)])


def public_projects(db: Session):
    return db.query(models.Project).filter(
        models.Project.is_public.is_(True), models.Project.archived_at.is_(None)
    )


@router.get("/", response_model=list[schemas.PublicProjectCard])
def list_public_projects(response: Response, db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = CACHE_CONTROL
    return public_projects(db).order_by(models.Project.name).all()


@router.get("/{slug}", response_model=schemas.PublicProject)
def read_public_project(slug: str, response: Response, db: Session = Depends(get_db)):
    project = public_projects(db).filter(models.Project.slug == slug).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    completed = (
        db.query(models.ProjectTask)
        .filter(
            models.ProjectTask.project_id == project.id,
            models.ProjectTask.status == TaskStatus.DONE,
            # Bugs et retours restent privés, même une fois traités.
            models.ProjectTask.kind == TaskKind.TASK,
            models.ProjectTask.archived_at.is_(None),
        )
        .order_by(models.ProjectTask.updated_at.desc())
        .limit(COMPLETED_TASKS_LIMIT)
        .all()
    )
    response.headers["Cache-Control"] = CACHE_CONTROL
    return schemas.PublicProject(
        **schemas.PublicProjectCard.model_validate(project).model_dump(),
        completed_tasks=[schemas.PublicCompletedTask.model_validate(task) for task in completed],
    )
