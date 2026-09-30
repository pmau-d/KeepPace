import csv
import io
from zoneinfo import ZoneInfo

from app import labels, models
from app.config import settings

HEADERS = [
    "Titre",
    "Client",
    "Entreprise",
    "Statut",
    "Statut personnalisé",
    "Priorité",
    "Échéance",
    "Présence client",
    "Commentaires",
    "Créée le",
    "Mise à jour le",
    "Description",
]

# Une cellule commençant par ces caractères serait interprétée comme une
# formule par Excel / LibreOffice (injection CSV).
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _cell(value) -> str:
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(_FORMULA_PREFIXES) else text


def tasks_to_csv(tasks: list[models.Task]) -> str:
    tz = ZoneInfo(settings.TIMEZONE)
    buffer = io.StringIO()
    # BOM + point-virgule : ouverture directe et correcte dans Excel en français.
    buffer.write("﻿")
    writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
    writer.writerow(HEADERS)
    for task in tasks:
        client = task.client
        writer.writerow(
            _cell(value)
            for value in (
                task.title,
                " ".join(p for p in (client.first_name, client.last_name) if p),
                client.company.name,
                labels.STATUS.get(task.status, task.status),
                task.sub_status,
                labels.PRIORITY.get(task.priority, task.priority),
                task.due_date.strftime("%d/%m/%Y") if task.due_date else "",
                labels.PRESENCE.get(client.presence_status, client.presence_status),
                task.comments_count,
                task.created_at.astimezone(tz).strftime("%d/%m/%Y %H:%M"),
                task.updated_at.astimezone(tz).strftime("%d/%m/%Y %H:%M"),
                task.description,
            )
        )
    return buffer.getvalue()
