"""Tâches à relancer aujourd'hui (vue « À relancer » et récap quotidien)."""

from datetime import timedelta

from sqlalchemy import and_, asc, case, nulls_last
from sqlalchemy.orm import Session, joinedload

from app import models
from app.enums import FollowUpReason, PresenceStatus, TaskPriority, TaskStatus
from app.presence import enrich_tasks, presence_status_expr, today
from app.repository import owned
from app.types import utcnow

# Ordre de priorité pour le tri : HIGH < MEDIUM < LOW (HIGH en premier)
PRIORITY_ORDER = case(
    (models.Task.priority == TaskPriority.HIGH, 1),
    (models.Task.priority == TaskPriority.MEDIUM, 2),
    (models.Task.priority == TaskPriority.LOW, 3),
    else_=4,
)

# Au-delà de ce délai sans mise à jour, une tâche « en attente client » est à relancer.
WAITING_DAYS = 3
FOLLOW_UP_LIMIT = 200
# Un client absent (ou pas encore rentré) ne peut pas être relancé.
UNREACHABLE = (PresenceStatus.ABSENT.value, PresenceStatus.SOON_BACK.value)
FOLLOW_UP_ORDER = list(FollowUpReason)


def follow_up_tasks(db: Session, user: models.User) -> list[models.Task]:
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
