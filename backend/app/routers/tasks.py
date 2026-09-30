from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import and_, asc, case, nulls_last, or_, select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.archive import archive_task, restore_task
from app.csv_export import tasks_to_csv
from app.database import get_db
from app.deps import get_current_user
from app.enums import FollowUpReason, PresenceStatus, TaskPriority, TaskStatus
from app.presence import enrich_task, enrich_tasks, presence_status_expr, today
from app.repository import get_client, get_task, owned
from app.types import utcnow

router = APIRouter(prefix="/tasks", tags=["tasks"])

TRACKED_FIELDS = ["status", "sub_status", "due_date", "description", "priority", "title", "client_id"]

# Ordre de priorité pour le tri : HIGH < MEDIUM < LOW (HIGH en premier)
PRIORITY_ORDER = case(
    (models.Task.priority == TaskPriority.HIGH, 1),
    (models.Task.priority == TaskPriority.MEDIUM, 2),
    (models.Task.priority == TaskPriority.LOW, 3),
    else_=4,
)


def _log(task: models.Task, field: str, old, new, comment: str | None = None, **labels) -> models.TaskLog:
    return models.TaskLog(
        task_id=task.id, field_changed=field, old_value=old, new_value=new, comment=comment, **labels
    )


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@dataclass
class TaskFilters:
    """Filtres communs à la liste et à l'export CSV."""

    client_id: Annotated[str | None, Query()] = None
    status: Annotated[TaskStatus | None, Query()] = None
    show_done: Annotated[bool, Query()] = False
    search: Annotated[str | None, Query(max_length=200, description="Titre, description et commentaires")] = (
        None
    )
    presence_status: Annotated[PresenceStatus | None, Query()] = None
    archived: Annotated[bool, Query()] = False

    def apply(self, query):
        if self.client_id:
            query = query.filter(models.Task.client_id == self.client_id)
        if self.status:
            query = query.filter(models.Task.status == self.status)
        if not self.show_done and self.status != TaskStatus.DONE:
            query = query.filter(models.Task.status != TaskStatus.DONE)
        if self.search and self.search.strip():
            pattern = f"%{_escape_like(self.search.strip())}%"
            in_comments = (
                select(models.TaskComment.id)
                .where(models.TaskComment.task_id == models.Task.id)
                .where(models.TaskComment.content.ilike(pattern, escape="\\"))
                .exists()
            )
            query = query.filter(
                or_(
                    models.Task.title.ilike(pattern, escape="\\"),
                    models.Task.description.ilike(pattern, escape="\\"),
                    in_comments,
                )
            )
        if self.presence_status:
            query = query.join(models.Client, models.Task.client_id == models.Client.id).filter(
                presence_status_expr(today()) == self.presence_status.value
            )
        return query


def _filtered_tasks(db: Session, user: models.User, filters: TaskFilters):
    query = filters.apply(owned(db, models.Task, user, archived=filters.archived))
    return query.options(joinedload(models.Task.client).joinedload(models.Client.company))


def _ordered(query):
    return query.order_by(
        # 1. Tâches avec date d'abord (NULL en dernier)
        nulls_last(asc(models.Task.due_date)),
        # 2. Priorité HIGH → MEDIUM → LOW
        asc(PRIORITY_ORDER),
        # 3. À égalité : plus récente d'abord, puis id pour une pagination stable
        models.Task.created_at.desc(),
        models.Task.id,
    )


@router.get("/", response_model=schemas.TaskPage)
def list_tasks(
    filters: TaskFilters = Depends(),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    query = _filtered_tasks(db, user, filters)
    total = query.order_by(None).count()
    tasks = _ordered(query).limit(limit).offset(offset).all()
    return {"items": enrich_tasks(db, tasks), "total": total, "limit": limit, "offset": offset}


# Au-delà de ce délai sans mise à jour, une tâche « en attente client » est à relancer.
WAITING_DAYS = 3
FOLLOW_UP_LIMIT = 200
# Un client absent (ou pas encore rentré) ne peut pas être relancé.
UNREACHABLE = (PresenceStatus.ABSENT.value, PresenceStatus.SOON_BACK.value)
FOLLOW_UP_ORDER = list(FollowUpReason)


@router.get("/follow-up", response_model=list[schemas.FollowUpItem])
def follow_up(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Tâches ouvertes à relancer aujourd'hui, les plus urgentes d'abord.

    Motifs, par ordre d'urgence : échéance dépassée, échéance aujourd'hui,
    client qui part dans les 3 jours, client rentré depuis moins de 5 jours,
    tâche en attente client sans mise à jour depuis 3 jours. Les clients
    absents ou pas encore rentrés sont exclus.
    """
    on = today()
    presence = presence_status_expr(on)
    rank = case(
        (models.Task.due_date < on, FOLLOW_UP_ORDER.index(FollowUpReason.OVERDUE)),
        (models.Task.due_date == on, FOLLOW_UP_ORDER.index(FollowUpReason.DUE_TODAY)),
        (presence == PresenceStatus.LEAVING_SOON.value, FOLLOW_UP_ORDER.index(FollowUpReason.CLIENT_LEAVING)),
        (presence == PresenceStatus.RECENTLY_BACK.value, FOLLOW_UP_ORDER.index(FollowUpReason.CLIENT_BACK)),
        (
            and_(
                models.Task.status == TaskStatus.BLOCKED,
                models.Task.updated_at < utcnow() - timedelta(days=WAITING_DAYS),
            ),
            FOLLOW_UP_ORDER.index(FollowUpReason.WAITING),
        ),
        else_=None,
    ).label("rank")
    rows = (
        owned(db, models.Task, user)
        .join(models.Client, models.Task.client_id == models.Client.id)
        .options(joinedload(models.Task.client).joinedload(models.Client.company))
        .filter(models.Task.status != TaskStatus.DONE, presence.not_in(UNREACHABLE), rank.is_not(None))
        .add_columns(rank)
        .order_by(rank, nulls_last(asc(models.Task.due_date)), asc(PRIORITY_ORDER), models.Task.id)
        .limit(FOLLOW_UP_LIMIT)
        .all()
    )
    tasks = enrich_tasks(db, [task for task, _ in rows])
    for task, (_, position) in zip(tasks, rows, strict=True):
        task.follow_up_reason = FOLLOW_UP_ORDER[position]
    return tasks


@router.get("/export.csv", response_class=Response, responses={200: {"content": {"text/csv": {}}}})
def export_csv(
    filters: TaskFilters = Depends(),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Exporte en CSV (Excel, séparateur « ; ») les tâches correspondant aux filtres de la liste."""
    tasks = enrich_tasks(db, _ordered(_filtered_tasks(db, user, filters)).all())
    filename = f"keeppace-taches-{today().isoformat()}.csv"
    return Response(
        content=tasks_to_csv(tasks),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
    return enrich_task(db, task)


@router.get("/{task_id}", response_model=schemas.TaskRead)
def read_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return enrich_task(db, get_task(db, task_id, user))


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
    new_client = get_client(db, update_data["client_id"], user) if update_data.get("client_id") else None

    # Une entrée d'audit par champ suivi réellement modifié
    for field in TRACKED_FIELDS:
        if field in update_data:
            old_val = str(getattr(task, field)) if getattr(task, field) is not None else None
            new_val = str(update_data[field]) if update_data[field] is not None else None
            if old_val == new_val:
                continue
            labels = {}
            if field == "client_id":
                labels = {"old_label": task.client.display_name, "new_label": new_client.display_name}
            db.add(_log(task, field, old_val, new_val, comment, **labels))

    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return enrich_task(db, task)


@router.post("/{task_id}/close", response_model=schemas.TaskRead)
def close_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Ferme la tâche (DONE) — réversible, conservée dans l'historique."""
    task = get_task(db, task_id, user)
    if task.status != TaskStatus.DONE:
        db.add(_log(task, "status", task.status, TaskStatus.DONE, "Tâche fermée"))
        task.status = TaskStatus.DONE
        db.commit()
        db.refresh(task)
    return enrich_task(db, task)


@router.post("/{task_id}/reopen", response_model=schemas.TaskRead)
def reopen_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Réouvre une tâche fermée → repasse en TODO."""
    task = get_task(db, task_id, user)
    if task.status == TaskStatus.DONE:
        db.add(_log(task, "status", TaskStatus.DONE, TaskStatus.TODO, "Tâche réouverte"))
        task.status = TaskStatus.TODO
        db.commit()
        db.refresh(task)
    return enrich_task(db, task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Archive la tâche : elle disparaît des listes mais garde tout son historique."""
    archive_task(db, get_task(db, task_id, user), "Tâche archivée")
    db.commit()


@router.post("/{task_id}/restore", response_model=schemas.TaskRead)
def restore(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    task = get_task(db, task_id, user, archived=True)
    if task.client.archived_at is not None:
        raise HTTPException(status_code=409, detail="Restaurez d'abord le client de cette tâche")
    restore_task(db, task)
    db.commit()
    db.refresh(task)
    return enrich_task(db, task)


@router.get("/{task_id}/logs", response_model=list[schemas.TaskLogRead])
def list_task_logs(
    task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    # L'historique reste consultable pour une tâche archivée.
    return get_task(db, task_id, user, archived=None).logs


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
    # Le contenu supprimé reste tracé dans le journal de la tâche.
    db.add(_log(task, "comment", comment.content, None, "Commentaire supprimé"))
    db.delete(comment)
    db.commit()
