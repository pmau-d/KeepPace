from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, case, nulls_last
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.utils import enrich_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

TRACKED_FIELDS = ["status", "sub_status", "due_date", "description", "priority", "title", "client_id"]

# Ordre de priorité pour le tri : HIGH < MEDIUM < LOW (HIGH en premier)
PRIORITY_ORDER = case(
    (models.Task.priority == "HIGH", 1),
    (models.Task.priority == "MEDIUM", 2),
    (models.Task.priority == "LOW", 3),
    else_=4,
)


def _presence_status_filter(query, presence_status: str, db: Session):
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
        cutoff = today + timedelta(days=3)
        return query.filter(models.Client.absence_end_date > cutoff)

    elif presence_status == "SOON_BACK":
        return query.filter(
            models.Client.absence_end_date >= today,
            models.Client.absence_end_date <= today + timedelta(days=3),
        )

    elif presence_status == "RECENTLY_BACK":
        return query.filter(
            models.Client.absence_end_date >= today - timedelta(days=5),
            models.Client.absence_end_date < today,
        )

    elif presence_status == "PRESENT":
        cutoff = today - timedelta(days=5)
        return query.filter(
            (models.Client.absence_end_date == None)  # noqa: E711
            | (models.Client.absence_end_date < cutoff)
        )

    return query


@router.get("/", response_model=list[schemas.TaskRead])
def get_tasks(
    client_id: str | None = Query(None),
    status: str | None = Query(None),
    show_done: bool = Query(False),
    search: str | None = Query(None),
    presence_status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Task)

    if client_id:
        query = query.filter(models.Task.client_id == client_id)
    if status:
        query = query.filter(models.Task.status == status)
    if not show_done:
        query = query.filter(models.Task.status != "DONE")
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
    if presence_status:
        query = _presence_status_filter(query, presence_status, db)

    return [
        enrich_task(t)
        for t in query.order_by(
            # 1. Tâches avec date d'abord (NULL en dernier)
            nulls_last(asc(models.Task.due_date)),
            # 2. Priorité HIGH → MEDIUM → LOW
            asc(PRIORITY_ORDER),
            # 3. À égalité : plus récente d'abord
            models.Task.created_at.desc(),
        ).all()
    ]


@router.post("/", response_model=schemas.TaskRead, status_code=201)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    task = models.Task(**data.model_dump())
    db.add(task)
    db.flush()

    # Log creation
    log = models.TaskLog(
        task_id=task.id,
        field_changed="status",
        old_value=None,
        new_value=task.status,
        comment="Tâche créée",
    )
    db.add(log)
    db.commit()
    db.refresh(task)
    return enrich_task(task)


@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return enrich_task(task)


@router.put("/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: str, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)
    comment = update_data.pop("comment", None)

    # Create audit logs for each tracked field that changed
    for field in TRACKED_FIELDS:
        if field in update_data:
            old_val = str(getattr(task, field)) if getattr(task, field) is not None else None
            new_val = str(update_data[field]) if update_data[field] is not None else None
            if old_val != new_val:
                log = models.TaskLog(
                    task_id=task.id,
                    field_changed=field,
                    old_value=old_val,
                    new_value=new_val,
                    comment=comment,
                )
                db.add(log)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return enrich_task(task)


@router.post("/{task_id}/close", response_model=schemas.TaskRead)
def close_task(task_id: str, db: Session = Depends(get_db)):
    """Ferme la tâche (DONE) — réversible, conservée dans l'historique."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "DONE":
        log = models.TaskLog(
            task_id=task.id,
            field_changed="status",
            old_value=task.status,
            new_value="DONE",
            comment="Tâche fermée",
        )
        db.add(log)
        task.status = "DONE"
        db.commit()
        db.refresh(task)
    return enrich_task(task)


@router.post("/{task_id}/reopen", response_model=schemas.TaskRead)
def reopen_task(task_id: str, db: Session = Depends(get_db)):
    """Réouvre une tâche fermée → repasse en TODO."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == "DONE":
        log = models.TaskLog(
            task_id=task.id,
            field_changed="status",
            old_value="DONE",
            new_value="TODO",
            comment="Tâche réouverte",
        )
        db.add(log)
        task.status = "TODO"
        db.commit()
        db.refresh(task)
    return enrich_task(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.get("/{task_id}/logs", response_model=list[schemas.TaskLogRead])
def get_task_logs(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.logs


@router.get("/{task_id}/comments", response_model=list[schemas.TaskCommentRead])
def get_task_comments(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.comments


@router.post("/{task_id}/comments", response_model=schemas.TaskCommentRead, status_code=201)
def add_task_comment(task_id: str, data: schemas.TaskCommentCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = models.TaskComment(task_id=task_id, content=data.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{task_id}/comments/{comment_id}", status_code=204)
def delete_task_comment(task_id: str, comment_id: str, db: Session = Depends(get_db)):
    comment = (
        db.query(models.TaskComment)
        .filter(
            models.TaskComment.id == comment_id,
            models.TaskComment.task_id == task_id,
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
