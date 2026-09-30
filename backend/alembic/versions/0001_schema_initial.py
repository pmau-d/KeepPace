"""Schéma initial (celui créé auparavant par create_all au démarrage)

Les bases existantes ont été créées par `Base.metadata.create_all()` puis
corrigées par des ALTER TABLE lancés à chaque démarrage. Cette révision
reproduit ce schéma pour une base neuve et, sur une base existante, se
contente d'appliquer ces deux correctifs une dernière fois.

Revision ID: 0001
Revises:
Create Date: 2026-09-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("tasks"):
        _upgrade_legacy_database(inspector)
        return

    op.create_table(
        "companies",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.UniqueConstraint("name", name="companies_name_key"),
    )
    op.create_table(
        "clients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("company_id", sa.String(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("absence_end_date", sa.Date(), nullable=True),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("sub_status", sa.String(), nullable=True),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "task_comments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("task_id", sa.String(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "task_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("task_id", sa.String(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_changed", sa.String(), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def _upgrade_legacy_database(inspector) -> None:
    """Les deux correctifs autrefois exécutés à chaque démarrage."""
    task_columns = {c["name"] for c in inspector.get_columns("tasks")}
    if "sub_status" not in task_columns:
        op.add_column("tasks", sa.Column("sub_status", sa.String(), nullable=True))
    if not inspector.has_table("task_comments"):
        op.create_table(
            "task_comments",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("task_id", sa.String(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        )
    last_name = next(c for c in inspector.get_columns("clients") if c["name"] == "last_name")
    if not last_name["nullable"]:
        with op.batch_alter_table("clients") as batch:
            batch.alter_column("last_name", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    for table in ("task_logs", "task_comments", "tasks", "clients", "companies"):
        op.drop_table(table)
