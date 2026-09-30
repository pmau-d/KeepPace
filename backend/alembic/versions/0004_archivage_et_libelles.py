"""Archivage (soft delete) et libellés lisibles dans le journal

- archived_at sur companies, clients et tasks : supprimer archive au lieu
  d'effacer, et l'historique des tâches est conservé ;
- old_label / new_label sur task_logs (ex. nom du client au lieu de son id) ;
- unicité du nom d'entreprise limitée aux entreprises actives (index
  partiel), pour pouvoir recréer une entreprise homonyme d'une archivée.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ARCHIVABLE = ("companies", "clients", "tasks")


def upgrade() -> None:
    for table in ARCHIVABLE:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    with op.batch_alter_table("task_logs") as batch:
        batch.add_column(sa.Column("old_label", sa.Text(), nullable=True))
        batch.add_column(sa.Column("new_label", sa.Text(), nullable=True))

    with op.batch_alter_table("companies") as batch:
        batch.drop_constraint("uq_companies_owner_name", type_="unique")
    op.create_index(
        "uq_companies_owner_name_active",
        "companies",
        ["owner_id", "name"],
        unique=True,
        postgresql_where=sa.text("archived_at IS NULL"),
        sqlite_where=sa.text("archived_at IS NULL"),
    )

    # Les anciens changements de client n'avaient que des ids : on reconstitue
    # les libellés à partir des clients existants.
    for side in ("old", "new"):
        op.execute(
            f"""
            UPDATE task_logs SET {side}_label = (
                SELECT TRIM(c.first_name || ' ' || COALESCE(c.last_name, '')) || ' · ' || co.name
                FROM clients c JOIN companies co ON co.id = c.company_id
                WHERE c.id = task_logs.{side}_value
            )
            WHERE field_changed = 'client_id' AND {side}_value IS NOT NULL
            """
        )


def downgrade() -> None:
    op.drop_index("uq_companies_owner_name_active", table_name="companies")
    with op.batch_alter_table("companies") as batch:
        batch.create_unique_constraint("uq_companies_owner_name", ["owner_id", "name"])
    with op.batch_alter_table("task_logs") as batch:
        batch.drop_column("new_label")
        batch.drop_column("old_label")
    for table in ARCHIVABLE:
        with op.batch_alter_table(table) as batch:
            batch.drop_column("archived_at")
