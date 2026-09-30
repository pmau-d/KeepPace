"""Libellés français (export CSV)."""

from app.enums import PresenceStatus, TaskPriority, TaskStatus

STATUS = {
    TaskStatus.TODO: "À faire",
    TaskStatus.IN_PROGRESS: "En cours",
    TaskStatus.BLOCKED: "En attente client",
    TaskStatus.DONE: "Terminé",
}
PRIORITY = {TaskPriority.HIGH: "Haute", TaskPriority.MEDIUM: "Moyenne", TaskPriority.LOW: "Basse"}
PRESENCE = {
    PresenceStatus.PRESENT: "Présent",
    PresenceStatus.LEAVING_SOON: "Bientôt absent",
    PresenceStatus.ABSENT: "Absent",
    PresenceStatus.SOON_BACK: "Bientôt de retour",
    PresenceStatus.RECENTLY_BACK: "Rentré récemment",
}
