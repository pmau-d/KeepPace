from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, case, nulls_last
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.enums import TaskPriority, TaskStatus
from app.repository import get_client, get_task, owned
from app.utils import enrich_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

TRACKED_FIELDS = ["status", "sub_status", "due_date", "description", "priority", "title", "client_id"]

# Ordre de priorité pour le tri : HIGH < MEDIUM < LOW (HIGH en premier)
PRIORITY_ORDER = case(
    (models.Task.priority == TaskPriority.HIGH, 1),
    (models.Task.priority == TaskPriority.MEDIUM, 2),
    (models.Task.priority == TaskPriority.LOW, 3),
    else_=4,
)


def _presence_status_filter(query, presence_status: str):
    """
    Filtre les tâches selon le statut de présence calculé de leur client.
    Le statut est calculé à partir de absence_end_date :
      ABSENT        : absence_end_date > today + 3 jours
      SOON_BACK     : 0 <= delta <= 3 jours
      RECENTLY_BACK : -5 <= delta < 0 jours
      PRESENT       : NULL ou delta < -5 jours
    """
    today = date.today()
    query = query.join(models.Client, models.Task.client_id == models.Client.id)

    if presence_status == "ABSENT":
        return query.filter(models.Client.absence_end_date > today + timedelta(days=3))
    if presence_status == "SOON_BACK":
        return query.filter(
            models.Client.absence_end_date >= today,
            models.Client.absence_end_date <= today + timedelta(days=3),
        )
    if presence_status == "RECENTLY_BACK":
        return query.filter(
            models.Client.absence_end_date >= today - timedelta(days=5),
            models.Client.absence_end_date < today,
        )
    if presence_status == "PRESENT":
        return query.filter(
            models.Client.absence_end_date.is_(None)
            | (models.Client.absence_end_date < today - timedelta(days=5))
        )
    return query


def _log(task: models.Task, field: str, old, new, comment: str | None = None) -> models.TaskLog:
    return models.TaskLog(task_id=task.id, field_changed=field, old_value=old, new_value=new, comment=comment)


@router.get("/", response_model=list[schemas.TaskRead])
def list_tasks(
    client_id: str | None = Query(None),
    status: TaskStatus | None = Query(None),
    show_done: bool = Query(False),
    search: str | None = Query(None),
    presence_status: str | None = Query(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    query = owned(db, models.Task, user)
    if client_id:
        query = query.filter(models.Task.client_id == client_id)
    if status:
        query = query.filter(models.Task.status == status)
    if not show_done:
        query = query.filter(models.Task.status != TaskStatus.DONE)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
    if presence_status:
        query = _presence_status_filter(query, presence_status)

    tasks = query.order_by(
        # 1. Tâches avec date d'abord (NULL en dernier)
        nulls_last(asc(models.Task.due_date)),
        # 2. Priorité HIGH → MEDIUM → LOW
        asc(PRIORITY_ORDER),
        # 3. À égalité : plus récente d'abord
        models.Task.created_at.desc(),
    ).all()
    return [enrich_task(t) for t in tasks]


@router.post("/", response_model=schemas.TaskRead, status_code=201)
def create_task(
    data: schemas.TaskCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    get_client(db, data.client_id, user)
    task = models.Task(**data.model_dump(), owner_id=user.id)
    db.add(task)
    db.flush()
    db.add(_log(task, "status", None, task.status, "Tâche créée"))
    db.commit()
    db.refresh(task)
    return enrich_task(task)


@router.get("/{task_id}", response_model=schemas.TaskRead)
def read_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return enrich_task(get_task(db, task_id, user))


@router.put("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: str,
    data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = get_task(db, task_id, user)
    update_data = data.model_dump(exclude_unset=True)
    comment = update_data.pop("comment", None)
    if update_data.get("client_id"):
        get_client(db, update_data["client_id"], user)

    # Une entrée d'audit par champ suivi réellement modifié
    for field in TRACKED_FIELDS:
        if field in update_data:
            old_val = str(getattr(task, field)) if getattr(task, field) is not None else None
            new_val = str(update_data[field]) if update_data[field] is not None else None
            if old_val != new_val:
                db.add(_log(task, field, old_val, new_val, comment))

    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return enrich_task(task)


@router.post("/{task_id}/close", response_model=schemas.TaskRead)
def close_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Ferme la tâche (DONE) — réversible, conservée dans l'historique."""
    task = get_task(db, task_id, user)
    if task.status != TaskStatus.DONE:
        db.add(_log(task, "status", task.status, TaskStatus.DONE, "Tâche fermée"))
        task.status = TaskStatus.DONE
        db.commit()
        db.refresh(task)
    return enrich_task(task)


@router.post("/{task_id}/reopen", response_model=schemas.TaskRead)
def reopen_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Réouvre une tâche fermée → repasse en TODO."""
    task = get_task(db, task_id, user)
    if task.status == TaskStatus.DONE:
        db.add(_log(task, "status", TaskStatus.DONE, TaskStatus.TODO, "Tâche réouverte"))
        task.status = TaskStatus.TODO
        db.commit()
        db.refresh(task)
    return enrich_task(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db.delete(get_task(db, task_id, user))
    db.commit()


@router.get("/{task_id}/logs", response_model=list[schemas.TaskLogRead])
def list_task_logs(
    task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    return get_task(db, task_id, user).logs


@router.get("/{task_id}/comments", response_model=list[schemas.TaskCommentRead])
def list_task_comments(
    task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    return get_task(db, task_id, user).comments


@router.post("/{task_id}/comments", response_model=schemas.TaskCommentRead, status_code=201)
def add_task_comment(
    task_id: str,
    data: schemas.TaskCommentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = get_task(db, task_id, user)
    comment = models.TaskComment(task_id=task.id, content=data.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{task_id}/comments/{comment_id}", status_code=204)
def delete_task_comment(
    task_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = get_task(db, task_id, user)
    comment = (
        db.query(models.TaskComment)
        .filter(models.TaskComment.id == comment_id, models.TaskComment.task_id == task.id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Commentaire introuvable")
    db.delete(comment)
    db.commit()
