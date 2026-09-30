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
