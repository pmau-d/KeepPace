"""Accès aux données toujours restreint à l'utilisateur connecté.

Une ressource d'un autre compte répond 404 (et non 403) pour ne pas révéler
qu'elle existe. Les objets archivés sont exclus sauf demande explicite.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def owned(db: Session, model, user: models.User, *, archived: bool | None = False):
    """archived=False : actifs seulement ; True : archivés seulement ; None : tous."""
    query = db.query(model).filter(model.owner_id == user.id)
    if archived is True:
        query = query.filter(model.archived_at.is_not(None))
    elif archived is False:
        query = query.filter(model.archived_at.is_(None))
    return query


def get_owned_or_404(db: Session, model, object_id: str, user: models.User, label: str, archived=False):
    obj = owned(db, model, user, archived=archived).filter(model.id == object_id).first()
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{label} introuvable")
    return obj


def get_company(db: Session, company_id: str, user: models.User, archived=False) -> models.Company:
    return get_owned_or_404(db, models.Company, company_id, user, "Entreprise", archived)


def get_client(db: Session, client_id: str, user: models.User, archived=False) -> models.Client:
    return get_owned_or_404(db, models.Client, client_id, user, "Client", archived)


def get_task(db: Session, task_id: str, user: models.User, archived=False) -> models.Task:
    return get_owned_or_404(db, models.Task, task_id, user, "Tâche", archived)
