"""Checklists des tâches (clientes et de projet) : le mode « check ticket »."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models

Task = models.Task | models.ProjectTask


def _parent(task: Task) -> dict[str, str]:
    key = "task_id" if isinstance(task, models.Task) else "project_task_id"
    return {key: task.id}


def add_item(db: Session, task: Task, label: str) -> models.ChecklistItem:
    position = max((item.position for item in task.checklist), default=-1) + 1
    item = models.ChecklistItem(**_parent(task), label=label, position=position)
    db.add(item)
    db.flush()
    return item


def get_item(task: Task, item_id: str) -> models.ChecklistItem:
    """L'élément doit appartenir à cette tâche : sinon 404, comme pour toute ressource d'autrui."""
    item = next((i for i in task.checklist if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément de checklist introuvable")
    return item


def copy_unchecked(db: Session, source: Task, target: Task) -> None:
    """Nouvelle occurrence d'une tâche récurrente : mêmes cases, toutes décochées."""
    for item in source.checklist:
        db.add(models.ChecklistItem(**_parent(target), label=item.label, position=item.position))
