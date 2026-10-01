"""Calcul de l'occurrence suivante d'une tâche récurrente."""

import calendar
from datetime import date, timedelta

from app.enums import Recurrence

LABELS = {
    Recurrence.DAILY: ("jour", "jours"),
    Recurrence.WEEKLY: ("semaine", "semaines"),
    Recurrence.MONTHLY: ("mois", "mois"),
    Recurrence.YEARLY: ("année", "ans"),
}


def _add_months(day: date, months: int) -> date:
    """Même jour du mois, borné au dernier jour (31 janv. + 1 mois = 28/29 févr.)."""
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def step(day: date, recurrence: Recurrence, interval: int, times: int = 1) -> date:
    n = interval * times
    if recurrence == Recurrence.DAILY:
        return day + timedelta(days=n)
    if recurrence == Recurrence.WEEKLY:
        return day + timedelta(weeks=n)
    if recurrence == Recurrence.MONTHLY:
        return _add_months(day, n)
    return _add_months(day, 12 * n)


def next_occurrence(due: date | None, recurrence: Recurrence, interval: int, today: date) -> date:
    """Prochaine échéance, toujours dans le futur.

    On part de l'échéance de l'occurrence terminée (ou d'aujourd'hui si elle
    n'en avait pas) pour garder le rythme (« le 5 de chaque mois »), en sautant
    les occurrences déjà passées si la tâche a été terminée en retard. Les
    échéances sont recalculées depuis le point de départ pour ne pas dériver
    (31 janv. → 28 févr. → 31 mars, et non 28 mars).
    """
    start = due or today
    times = 1
    while (candidate := step(start, recurrence, interval, times)) <= today:
        times += 1
    return candidate


def describe(recurrence: Recurrence, interval: int) -> str:
    singular, plural = LABELS[recurrence]
    if interval <= 1:
        return f"chaque {singular}"
    every = "toutes les" if recurrence == Recurrence.WEEKLY else "tous les"  # « semaine » est féminin
    return f"{every} {interval} {plural}"
