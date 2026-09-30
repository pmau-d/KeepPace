"""Crée un compte de démonstration rempli de données fictives.

    docker compose exec backend python -m scripts.seed_demo
    # ou, en local : python -m scripts.seed_demo

Toutes les entreprises, personnes et adresses sont inventées (domaine réservé
example.com). Le script refuse de s'exécuter en production et n'écrase rien :
il s'arrête si le compte de démonstration existe déjà.
"""

import os
from datetime import timedelta

from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import SessionLocal
from app.enums import TaskPriority, TaskStatus
from app.presence import today
from app.security import hash_password
from app.types import utcnow

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo-keeppace-2026")

# (entreprise, prénom, nom, début d'absence, fin d'absence) — décalages en jours
CLIENTS = [
    ("Atelier Boréal", "Camille", "Durand", None, None),
    ("Atelier Boréal", "Hugo", "Lefèvre", -10, 8),
    ("Brasserie du Quai", "Inès", "Moreau", 2, 12),
    ("Brasserie du Quai", "Nathan", None, None, -2),
    ("Studio Nimbus", "Léa", "Garnier", None, None),
    ("Transports Orion", "Malik", "Robert", None, None),
]

# (index client, titre, statut, priorité, échéance en jours, statut personnalisé, description)
TASKS = [
    (
        0,
        "Envoyer la proposition commerciale",
        TaskStatus.IN_PROGRESS,
        TaskPriority.HIGH,
        -2,
        None,
        "Version 2 avec le lot optionnel.",
    ),
    (0, "Préparer l'atelier de lancement", TaskStatus.TODO, TaskPriority.MEDIUM, 6, None, None),
    (
        1,
        "Valider le cahier des charges",
        TaskStatus.BLOCKED,
        TaskPriority.HIGH,
        9,
        "En attente de validation",
        None,
    ),
    (
        2,
        "Faire signer le bon de commande",
        TaskStatus.TODO,
        TaskPriority.HIGH,
        1,
        None,
        "À obtenir avant son départ.",
    ),
    (3, "Point d'étape après ses congés", TaskStatus.TODO, TaskPriority.MEDIUM, None, None, None),
    (4, "Relire la maquette de la page d'accueil", TaskStatus.IN_PROGRESS, TaskPriority.LOW, 0, None, None),
    (
        5,
        "Chiffrer l'extension du périmètre",
        TaskStatus.BLOCKED,
        TaskPriority.MEDIUM,
        14,
        "En attente de chiffrage",
        None,
    ),
    (5, "Mettre à jour le planning", TaskStatus.TODO, TaskPriority.LOW, 21, None, None),
    (5, "Facturer la phase 1", TaskStatus.DONE, TaskPriority.MEDIUM, -5, None, None),
]

COMMENTS = {
    0: ["Appel le 24 : intéressée, attend le détail du lot optionnel."],
    2: ["Relance envoyée par email.", "Réponse promise pour la fin de semaine."],
}


def seed(db: Session) -> models.User:
    if settings.ENVIRONMENT == "production":
        raise SystemExit("Refusé : pas de données de démonstration en production.")
    if db.query(models.User).filter(models.User.email == DEMO_EMAIL).first():
        raise SystemExit(f"Le compte {DEMO_EMAIL} existe déjà : rien à faire.")

    user = models.User(
        email=DEMO_EMAIL, full_name="Compte de démonstration", password_hash=hash_password(DEMO_PASSWORD)
    )
    db.add(user)
    db.flush()

    on = today()
    companies: dict[str, models.Company] = {}
    clients = []
    for company_name, first, last, start, end in CLIENTS:
        company = companies.get(company_name)
        if company is None:
            company = companies[company_name] = models.Company(name=company_name, owner_id=user.id)
            db.add(company)
            db.flush()
        slug = first.lower().replace("è", "e").replace("é", "e")
        client = models.Client(
            owner_id=user.id,
            company_id=company.id,
            first_name=first,
            last_name=last,
            email=f"{slug}@example.com",
            absence_start_date=on + timedelta(days=start) if start is not None else None,
            absence_end_date=on + timedelta(days=end) if end is not None else None,
        )
        db.add(client)
        clients.append(client)
    db.flush()

    for index, (client_index, title, status, priority, due, sub_status, description) in enumerate(TASKS):
        task = models.Task(
            owner_id=user.id,
            client_id=clients[client_index].id,
            title=title,
            status=status,
            priority=priority,
            due_date=on + timedelta(days=due) if due is not None else None,
            sub_status=sub_status,
            description=description,
        )
        db.add(task)
        db.flush()
        db.add(
            models.TaskLog(
                task_id=task.id, field_changed="status", new_value=TaskStatus.TODO, comment="Tâche créée"
            )
        )
        if status != TaskStatus.TODO:
            db.add(
                models.TaskLog(
                    task_id=task.id, field_changed="status", old_value=TaskStatus.TODO, new_value=status
                )
            )
        for content in COMMENTS.get(index, []):
            db.add(models.TaskComment(task_id=task.id, content=content))
        if status == TaskStatus.BLOCKED:
            # Sans nouvelle depuis une semaine : apparaît dans « À relancer ».
            task.updated_at = utcnow() - timedelta(days=7)

    db.commit()
    return user


def main() -> None:
    with SessionLocal() as db:
        seed(db)
    print(f"Compte de démonstration créé : {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
