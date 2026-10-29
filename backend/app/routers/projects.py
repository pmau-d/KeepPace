from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.archive import archive_project, restore_project
from app.database import get_db
from app.deps import get_current_user
from app.projects import public_address_taken, unique_slug
from app.repository import get_project, owned

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[schemas.ProjectRead])
def list_projects(
    archived: bool = False, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    return owned(db, models.Project, user, archived=archived).order_by(models.Project.name).all()


@router.post("/", response_model=schemas.ProjectRead, status_code=201)
def create_project(
    data: schemas.ProjectCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    project = models.Project(**data.model_dump(), owner_id=user.id, slug=unique_slug(db, user.id, data.name))
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=schemas.ProjectRead)
def read_project(
    project_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    return get_project(db, project_id, user)


@router.put("/{project_id}", response_model=schemas.ProjectRead)
def update_project(
    project_id: str,
    data: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    project = get_project(db, project_id, user)
    # Le slug ne change pas au renommage : les liens déjà partagés restent valides.
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None or field == "description":
            setattr(project, field, value)
    if project.is_public and public_address_taken(db, project):
        db.rollback()
        raise HTTPException(
            status_code=409, detail=f"Un autre projet public utilise déjà l'adresse « {project.slug} »"
        )
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    """Archive le projet et ses tâches (réversible)."""
    archive_project(db, get_project(db, project_id, user))
    db.commit()


@router.post("/{project_id}/restore", response_model=schemas.ProjectRead)
def restore(project_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    project = get_project(db, project_id, user, archived=True)
    restore_project(db, project)
    # L'adresse a pu être prise pendant l'archivage : le projet revient en privé.
    if project.is_public and public_address_taken(db, project):
        project.is_public = False
    db.commit()
    db.refresh(project)
    return project
