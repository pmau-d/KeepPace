from fastapi import APIRouter, Depends
from sqlalchemy import asc, case, nulls_last
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.enums import TaskKind, TaskPriority, TaskStatus
from app.presence import today
from app.recurrence import next_occurrence
from app.repository import get_project, get_project_task, owned
from app.types import utcnow

router = APIRouter(prefix="/project-tasks", tags=["project-tasks"])

PRIORITY_ORDER = case(
    (models.ProjectTask.priority == TaskPriority.HIGH, 1),
    (models.ProjectTask.priority == TaskPriority.MEDIUM, 2),
    (models.ProjectTask.priority == TaskPriority.LOW, 3),
    else_=4,
)

# Champs qui ne peuvent pas être vidés : un null explicite est ignoré.
REQUIRED = {"title", "kind", "status", "priority", "recurrence_interval"}


def _spawn_next_occurrence(task: models.ProjectTask, db: Session) -> None:
    """Terminer une tâche récurrente crée l'occurrence suivante, une seule fois."""
    if task.recurrence is None or task.archived_at is not None or task.recurred_at is not None:
        return
    db.add(
        models.ProjectTask(
            owner_id=task.owner_id,
            project_id=task.project_id,
            kind=task.kind,
            title=task.title,
            description=task.description,
            priority=task.priority,
            status=TaskStatus.TODO,
            due_date=next_occurrence(task.due_date, task.recurrence, task.recurrence_interval, today()),
            recurrence=task.recurrence,
            recurrence_interval=task.recurrence_interval,
        )
    )
    task.recurred_at = utcnow()


@router.get("/", response_model=list[schemas.ProjectTaskRead])
def list_project_tasks(
    project_id: str | None = None,
    kind: TaskKind | None = None,
    show_done: bool = False,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    query = owned(db, models.ProjectTask, user)
    # Les tâches d'un projet archivé sont archivées avec lui (voir app/archive.py).
    if project_id:
        query = query.filter(models.ProjectTask.project_id == project_id)
    if kind:
        query = query.filter(models.ProjectTask.kind == kind)
    if not show_done:
        query = query.filter(models.ProjectTask.status != TaskStatus.DONE)
    return query.order_by(
        nulls_last(asc(models.ProjectTask.due_date)),
        asc(PRIORITY_ORDER),
        models.ProjectTask.created_at.desc(),
        models.ProjectTask.id,
    ).all()


@router.post("/", response_model=schemas.ProjectTaskRead, status_code=201)
def create_project_task(
    data: schemas.ProjectTaskCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    get_project(db, data.project_id, user)
    task = models.ProjectTask(**data.model_dump(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=schemas.ProjectTaskRead)
def update_project_task(
    task_id: str,
    data: schemas.ProjectTaskUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = get_project_task(db, task_id, user)
    changes = {
        k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None or k not in REQUIRED
    }
    completed = changes.get("status") == TaskStatus.DONE and task.status != TaskStatus.DONE
    for field, value in changes.items():
        setattr(task, field, value)
    if completed:
        _spawn_next_occurrence(task, db)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/close", response_model=schemas.ProjectTaskRead)
def close_project_task(
    task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    task = get_project_task(db, task_id, user)
    if task.status != TaskStatus.DONE:
        task.status = TaskStatus.DONE
        _spawn_next_occurrence(task, db)
        db.commit()
        db.refresh(task)
    return task


@router.post("/{task_id}/reopen", response_model=schemas.ProjectTaskRead)
def reopen_project_task(
    task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    task = get_project_task(db, task_id, user)
    if task.status == TaskStatus.DONE:
        task.status = TaskStatus.TODO
        db.commit()
        db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_project_task(
    task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    """Archive la tâche : elle disparaît des listes et de l'avancement."""
    get_project_task(db, task_id, user).archived_at = utcnow()
    db.commit()
