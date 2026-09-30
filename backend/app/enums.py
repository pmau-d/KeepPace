from enum import StrEnum


class TaskStatus(StrEnum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"


class TaskPriority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PresenceStatus(StrEnum):
    """Voir app/presence.py pour la règle de calcul."""

    PRESENT = "PRESENT"
    LEAVING_SOON = "LEAVING_SOON"
    ABSENT = "ABSENT"
    SOON_BACK = "SOON_BACK"
    RECENTLY_BACK = "RECENTLY_BACK"


class FollowUpReason(StrEnum):
    """Pourquoi une tâche apparaît dans « À relancer aujourd'hui », par urgence."""

    OVERDUE = "OVERDUE"  # échéance dépassée
    DUE_TODAY = "DUE_TODAY"  # échéance aujourd'hui
    CLIENT_LEAVING = "CLIENT_LEAVING"  # le client part bientôt : le joindre avant
    CLIENT_BACK = "CLIENT_BACK"  # le client vient de rentrer
    WAITING = "WAITING"  # en attente client sans nouvelle depuis plusieurs jours
