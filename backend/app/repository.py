"""Accès aux données toujours restreint à l'utilisateur connecté.

Une ressource d'un autre compte répond 404 (et non 403) pour ne pas révéler
qu'elle existe.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def owned(db: Session, model, user: models.User):
    return db.query(model).filter(model.owner_id == user.id)


def get_owned_or_404(db: Session, model, object_id: str, user: models.User, label: str):
    obj = owned(db, model, user).filter(model.id == object_id).first()
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{label} introuvable")
    return obj


def get_company(db: Session, company_id: str, user: models.User) -> models.Company:
    return get_owned_or_404(db, models.Company, company_id, user, "Entreprise")


def get_client(db: Session, client_id: str, user: models.User) -> models.Client:
    return get_owned_or_404(db, models.Client, client_id, user, "Client")


def get_task(db: Session, task_id: str, user: models.User) -> models.Task:
    return get_owned_or_404(db, models.Task, task_id, user, "Tâche")
