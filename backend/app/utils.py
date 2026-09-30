from datetime import date


def compute_presence_status(absence_end_date) -> str:
    """
    Calcule le statut de présence dynamiquement à partir de absence_end_date.
    🔴 ABSENT        : absence_end_date > today + 3 jours
    🟡 SOON_BACK     : 0 <= delta <= 3 jours
    🔵 RECENTLY_BACK : -5 <= delta < 0 jours
    🟢 PRESENT       : NULL ou delta < -5 jours
    """
    if absence_end_date is None:
        return "PRESENT"
    today = date.today()
    delta = (absence_end_date - today).days
    if delta > 3:
        return "ABSENT"
    elif 0 <= delta <= 3:
        return "SOON_BACK"
    elif -5 <= delta < 0:
        return "RECENTLY_BACK"
    else:
        return "PRESENT"


def enrich_client(client):
    """Attache le presence_status calculé à un objet Client SQLAlchemy."""
    client.presence_status = compute_presence_status(client.absence_end_date)
    return client


def enrich_task(task):
    """Enrichit le client imbriqué dans une tâche."""
    enrich_client(task.client)
    return task

