"""Récap quotidien : à relancer aujourd'hui, départs et retours de clients.

Affiché dans l'application (GET /digest) et, si le serveur l'autorise
(DIGEST_ENABLED + SMTP), envoyé chaque matin aux comptes qui l'ont activé.
"""

import logging
import smtplib
import ssl
import threading
from collections import Counter
from datetime import datetime, timedelta
from email.message import EmailMessage
from html import escape
from zoneinfo import ZoneInfo

from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import SessionLocal
from app.enums import FollowUpReason
from app.follow_up import follow_up_tasks
from app.presence import LEAVING_SOON_DAYS, SOON_BACK_DAYS, today
from app.repository import owned

logger = logging.getLogger("keeppace.digest")

REASONS = {
    FollowUpReason.OVERDUE: "Échéance dépassée",
    FollowUpReason.DUE_TODAY: "Échéance aujourd'hui",
    FollowUpReason.CLIENT_LEAVING: "Le client part bientôt",
    FollowUpReason.CLIENT_BACK: "Le client vient de rentrer",
    FollowUpReason.WAITING: "En attente sans nouvelle",
}
EMAIL_ITEMS = 20


def build_digest(db: Session, user: models.User) -> schemas.Digest:
    on = today()
    tasks = follow_up_tasks(db, user)
    clients = owned(db, models.Client, user)
    leaving = clients.filter(
        models.Client.absence_start_date > on,
        models.Client.absence_start_date <= on + timedelta(days=LEAVING_SOON_DAYS),
    )
    # Retour = lendemain du dernier jour d'absence
    returning = clients.filter(
        models.Client.absence_end_date >= on - timedelta(days=1),
        models.Client.absence_end_date < on + timedelta(days=SOON_BACK_DAYS),
        or_(models.Client.absence_start_date.is_(None), models.Client.absence_start_date <= on),
    )

    def entry(client: models.Client, day) -> schemas.DigestClient:
        return schemas.DigestClient(id=client.id, name=client.display_name, on=day)

    return schemas.Digest(
        day=on,
        follow_up=[schemas.FollowUpItem.model_validate(t) for t in tasks],
        follow_up_total=len(tasks),
        counts=dict(Counter(t.follow_up_reason for t in tasks)),
        leaving=[entry(c, c.absence_start_date) for c in leaving.order_by(models.Client.absence_start_date)],
        returning=[
            entry(c, c.absence_end_date + timedelta(days=1))
            for c in returning.order_by(models.Client.absence_end_date)
        ],
        email_available=settings.email_enabled,
    )


def _format_day(day) -> str:
    return day.strftime("%d/%m")


def render_email(user: models.User, digest: schemas.Digest) -> EmailMessage:
    """Version texte et HTML du récap (styles en ligne, lisible sans images)."""
    total = digest.follow_up_total
    subject = (
        f"KeepPace · {total} relance{'s' if total > 1 else ''} aujourd'hui"
        if total
        else "KeepPace · rien à relancer aujourd'hui"
    )
    greeting = f"Bonjour {user.full_name}," if user.full_name else "Bonjour,"
    lines = [greeting, ""]
    html = [f"<p>{escape(greeting)}</p>"]

    if total:
        lines.append(f"À relancer aujourd'hui ({total}) :")
        html.append(f"<h2 style='font-size:16px'>À relancer aujourd'hui ({total})</h2><ul>")
        for task in digest.follow_up[:EMAIL_ITEMS]:
            reason = REASONS[task.follow_up_reason]
            client = f"{task.client.first_name} {task.client.last_name or ''}".strip()
            lines.append(f"- {task.title} — {client} ({reason})")
            html.append(
                f"<li><strong>{escape(task.title)}</strong> — {escape(client)} "
                f"<span style='color:#64748b'>({escape(reason)})</span></li>"
            )
        if total > EMAIL_ITEMS:
            lines.append(f"… et {total - EMAIL_ITEMS} autre(s).")
            html.append(f"<li>… et {total - EMAIL_ITEMS} autre(s).</li>")
        html.append("</ul>")
    for title, people, verb in (
        ("Partent bientôt", digest.leaving, "part le"),
        ("Reviennent bientôt", digest.returning, "de retour le"),
    ):
        if people:
            lines += ["", f"{title} :"] + [f"- {p.name}, {verb} {_format_day(p.on)}" for p in people if p.on]
            html.append(f"<h2 style='font-size:16px'>{title}</h2><ul>")
            html += [f"<li>{escape(p.name)}, {verb} {_format_day(p.on)}</li>" for p in people if p.on]
            html.append("</ul>")

    link = f"{settings.APP_URL.rstrip('/')}/relances"
    lines += ["", f"Ouvrir KeepPace : {link}", "", "Désactivez ce récap depuis le menu de votre compte."]
    html.append(
        f"<p><a href='{escape(link)}' style='color:#4f46e5'>Ouvrir KeepPace</a></p>"
        "<p style='color:#94a3b8;font-size:12px'>Désactivez ce récap depuis le menu de votre compte.</p>"
    )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM
    message["To"] = user.email
    message.set_content("\n".join(lines))
    message.add_alternative(
        "<div style='font-family:system-ui,sans-serif;color:#1e293b'>" + "".join(html) + "</div>",
        subtype="html",
    )
    return message


def send_email(message: EmailMessage) -> None:
    context = ssl.create_default_context()
    smtp_class = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    kwargs = {"context": context} if settings.SMTP_SSL else {}
    with smtp_class(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15, **kwargs) as smtp:
        if settings.SMTP_STARTTLS and not settings.SMTP_SSL:
            smtp.starttls(context=context)
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)


def send_digest(db: Session, user: models.User) -> bool:
    """Envoie le récap s'il y a quelque chose à signaler. Renvoie True si un email est parti."""
    digest = build_digest(db, user)
    if digest.is_empty:
        return False
    send_email(render_email(user, digest))
    return True


def send_all_digests(db: Session) -> int:
    users = db.query(models.User).filter(and_(models.User.is_active, models.User.digest_opt_in)).all()
    sent = 0
    for user in users:
        try:
            sent += send_digest(db, user)
        except Exception:  # un compte en échec ne bloque pas les autres
            logger.exception("Récap non envoyé à l'utilisateur %s", user.id)
    return sent


def _scheduler_loop(stop: threading.Event) -> None:
    """Un envoi par jour à DIGEST_HOUR (heure locale de TIMEZONE)."""
    last_day = None
    zone = ZoneInfo(settings.TIMEZONE)
    while not stop.wait(60):
        now = datetime.now(zone)
        if now.hour == settings.DIGEST_HOUR and now.date() != last_day:
            last_day = now.date()
            with SessionLocal() as db:
                count = send_all_digests(db)
            logger.info("Récap quotidien : %s email(s) envoyé(s)", count)


def start_scheduler() -> threading.Event | None:
    """Démarre l'envoi quotidien dans un fil de fond. Avec plusieurs processus
    uvicorn, un verrou PostgreSQL garantit un seul envoi (voir _acquire_lock)."""
    if not settings.email_enabled or settings.ENVIRONMENT == "test":
        return None
    stop = threading.Event()
    threading.Thread(target=_locked_loop, args=(stop,), name="digest", daemon=True).start()
    return stop


def _locked_loop(stop: threading.Event) -> None:
    # Un seul processus envoie : le premier qui obtient le verrou consultatif.
    with SessionLocal() as db:
        if db.bind.dialect.name == "postgresql":
            while not db.execute(text("SELECT pg_try_advisory_lock(7331)")).scalar():
                if stop.wait(300):
                    return
        _scheduler_loop(stop)
