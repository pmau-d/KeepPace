"""Statut et priorité contraints, horodatages avec fuseau horaire

- status / priority : contrainte CHECK sur les valeurs connues (les valeurs
  inconnues éventuelles sont d'abord ramenées à TODO / MEDIUM) ;
- created_at / updated_at : `timestamptz`, en interprétant les valeurs
  existantes comme de l'UTC (fuseau par défaut du conteneur PostgreSQL).

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATUSES = ("TODO", "IN_PROGRESS", "BLOCKED", "DONE")
PRIORITIES = ("HIGH", "MEDIUM", "LOW")
TIMESTAMPS = {
    "tasks": ("created_at", "updated_at"),
    "task_comments": ("created_at",),
    "task_logs": ("created_at",),
}


def _in(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    op.execute(f"UPDATE tasks SET status = 'TODO' WHERE status IS NULL OR status NOT IN ({_in(STATUSES)})")
    op.execute(
        f"UPDATE tasks SET priority = 'MEDIUM' WHERE priority IS NULL OR priority NOT IN ({_in(PRIORITIES)})"
    )
    for table, columns in TIMESTAMPS.items():
        for column in columns:
            op.execute(f"UPDATE {table} SET {column} = CURRENT_TIMESTAMP WHERE {column} IS NULL")

    with op.batch_alter_table("tasks") as batch:
        batch.alter_column("status", existing_type=sa.String(), type_=sa.String(20))
        batch.alter_column("priority", existing_type=sa.String(), type_=sa.String(20))
        batch.create_check_constraint("task_status", f"status IN ({_in(STATUSES)})")
        batch.create_check_constraint("task_priority", f"priority IN ({_in(PRIORITIES)})")

    for table, columns in TIMESTAMPS.items():
        with op.batch_alter_table(table) as batch:
            for column in columns:
                batch.alter_column(
                    column,
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    nullable=False,
                    existing_server_default=sa.func.now(),
                    **({"postgresql_using": f"{column} AT TIME ZONE 'UTC'"} if is_postgres else {}),
                )


def downgrade() -> None:
    for table, columns in TIMESTAMPS.items():
        with op.batch_alter_table(table) as batch:
            for column in columns:
                batch.alter_column(
                    column,
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    nullable=True,
                    existing_server_default=sa.func.now(),
                )
    with op.batch_alter_table("tasks") as batch:
        batch.drop_constraint("task_priority", type_="check")
        batch.drop_constraint("task_status", type_="check")
        batch.alter_column("status", existing_type=sa.String(20), type_=sa.String())
        batch.alter_column("priority", existing_type=sa.String(20), type_=sa.String())
