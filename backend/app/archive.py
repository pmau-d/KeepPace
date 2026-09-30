"""Archivage en cascade et restauration.

Un archivage en cascade (entreprise → clients → tâches) utilise le même
horodatage pour tous les objets concernés : la restauration ne réactive que
ce qui a été archivé en même temps, pas ce qui l'était déjà avant.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.types import utcnow

ARCHIVED_FIELD = "archived"


def _log(task: models.Task, archived: bool, reason: str) -> models.TaskLog:
    return models.TaskLog(
        task_id=task.id,
        field_changed=ARCHIVED_FIELD,
        old_value=None if archived else "true",
        new_value="true" if archived else None,
        comment=reason,
    )


def archive_task(db: Session, task: models.Task, reason: str, at: datetime | None = None) -> None:
    task.archived_at = at or utcnow()
    db.add(_log(task, True, reason))


def restore_task(db: Session, task: models.Task, reason: str = "Tâche restaurée") -> None:
    task.archived_at = None
    db.add(_log(task, False, reason))


def archive_client(db: Session, client: models.Client, at: datetime | None = None) -> None:
    at = at or utcnow()
    client.archived_at = at
    for task in client.tasks:
        if task.archived_at is None:
            archive_task(db, task, f"Client archivé : {client.display_name}", at)


def restore_client(db: Session, client: models.Client) -> None:
    at = client.archived_at
    client.archived_at = None
    for task in client.tasks:
        if task.archived_at == at:
            restore_task(db, task, f"Client restauré : {client.display_name}")


def archive_company(db: Session, company: models.Company) -> None:
    at = utcnow()
    company.archived_at = at
    for client in company.clients:
        if client.archived_at is None:
            archive_client(db, client, at)


def restore_company(db: Session, company: models.Company) -> None:
    at = company.archived_at
    company.archived_at = None
    for client in company.clients:
        if client.archived_at == at:
            restore_client(db, client)
