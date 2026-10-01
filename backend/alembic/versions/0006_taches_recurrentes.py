"""Tâches récurrentes

Terminer une tâche récurrente crée l'occurrence suivante. `recurrence` vaut
NULL pour une tâche ponctuelle.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RECURRENCES = ("DAILY", "WEEKLY", "MONTHLY", "YEARLY")


def upgrade() -> None:
    with op.batch_alter_table("tasks") as batch:
        batch.add_column(sa.Column("recurrence", sa.String(length=20), nullable=True))
        batch.add_column(sa.Column("recurrence_interval", sa.Integer(), nullable=False, server_default="1"))
        values = ", ".join(f"'{value}'" for value in RECURRENCES)
        batch.create_check_constraint("task_recurrence", f"recurrence IN ({values})")


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch:
        batch.drop_constraint("task_recurrence", type_="check")
        batch.drop_column("recurrence_interval")
        batch.drop_column("recurrence")
