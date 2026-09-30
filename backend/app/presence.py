"""Statut de présence des clients — source de vérité unique.

La règle n'existe qu'ici, sous forme d'expression SQL : elle sert à la fois à
filtrer (WHERE) et à renvoyer le statut calculé dans l'API, ce qui évite les
divergences entre un calcul Python et un filtre SQL.

Période d'absence : [absence_start_date, absence_end_date], chaque borne
étant optionnelle (début vide = absence déjà commencée ; fin vide = retour
non daté).

  🟢 PRESENT       aucune absence, absence lointaine, ou retour il y a > 5 j
  🟠 LEAVING_SOON  l'absence commence dans les 3 prochains jours
  🔴 ABSENT        absence en cours, retour dans plus de 3 jours ou non daté
  🟡 SOON_BACK     absence en cours, retour dans 0 à 3 jours
  🔵 RECENTLY_BACK retour dans les 5 derniers jours
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import and_, case, literal, select
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.enums import PresenceStatus

LEAVING_SOON_DAYS = 3
SOON_BACK_DAYS = 3
RECENTLY_BACK_DAYS = 5


def today() -> date:
    """« Aujourd'hui » dans le fuseau de l'utilisateur, pas celui du serveur."""
    return datetime.now(ZoneInfo(settings.TIMEZONE)).date()


def presence_status_expr(on: date):
    start = models.Client.absence_start_date
    end = models.Client.absence_end_date
    status = {s: literal(s.value) for s in PresenceStatus}
    return case(
        (and_(start.is_(None), end.is_(None)), status[PresenceStatus.PRESENT]),
        (
            and_(start.is_not(None), start > on + timedelta(days=LEAVING_SOON_DAYS)),
            status[PresenceStatus.PRESENT],
        ),
        (and_(start.is_not(None), start > on), status[PresenceStatus.LEAVING_SOON]),
        # L'absence a commencé (ou n'a pas de date de début)
        (end.is_(None), status[PresenceStatus.ABSENT]),
        (end > on + timedelta(days=SOON_BACK_DAYS), status[PresenceStatus.ABSENT]),
        (end >= on, status[PresenceStatus.SOON_BACK]),
        (end >= on - timedelta(days=RECENTLY_BACK_DAYS), status[PresenceStatus.RECENTLY_BACK]),
        else_=status[PresenceStatus.PRESENT],
    )


def attach_presence(db: Session, clients) -> None:
    """Calcule en une requête le statut de présence d'une liste de clients."""
    clients = [c for c in clients if c is not None]
    if not clients:
        return
    rows = db.execute(
        select(models.Client.id, presence_status_expr(today())).where(
            models.Client.id.in_({c.id for c in clients})
        )
    ).all()
    statuses = dict(rows)
    for client in clients:
        client.presence_status = statuses.get(client.id)


def enrich_client(db: Session, client: models.Client) -> models.Client:
    attach_presence(db, [client])
    return client


def enrich_clients(db: Session, clients: list[models.Client]) -> list[models.Client]:
    attach_presence(db, clients)
    return clients


def enrich_task(db: Session, task: models.Task) -> models.Task:
    attach_presence(db, [task.client])
    return task


def enrich_tasks(db: Session, tasks: list[models.Task]) -> list[models.Task]:
    attach_presence(db, {t.client.id: t.client for t in tasks}.values())
    return tasks
