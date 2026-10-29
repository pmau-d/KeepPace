"""Projets de développement et leurs tâches typées

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _in(column: str, values: Sequence[str]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


def upgrade() -> None:
    timestamp = sa.DateTime(timezone=True)
    op.create_table(
        "projects",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", timestamp, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", timestamp, nullable=False, server_default=sa.func.now()),
        sa.Column("archived_at", timestamp, nullable=True),
        sa.UniqueConstraint("owner_id", "slug", name="uq_projects_owner_slug"),
        sa.CheckConstraint(_in("status", ("IDEA", "ACTIVE", "PAUSED", "DELIVERED")), name="project_status"),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])

    op.create_table(
        "project_tasks",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("recurrence", sa.String(length=20), nullable=True),
        sa.Column("recurrence_interval", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", timestamp, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", timestamp, nullable=False, server_default=sa.func.now()),
        sa.Column("archived_at", timestamp, nullable=True),
        sa.Column("recurred_at", timestamp, nullable=True),
        sa.CheckConstraint(_in("kind", ("TASK", "BUG", "IMPROVEMENT")), name="project_task_kind"),
        sa.CheckConstraint(
            _in("status", ("TODO", "IN_PROGRESS", "BLOCKED", "DONE")), name="project_task_status"
        ),
        sa.CheckConstraint(_in("priority", ("HIGH", "MEDIUM", "LOW")), name="project_task_priority"),
        sa.CheckConstraint(
            _in("recurrence", ("DAILY", "WEEKLY", "MONTHLY", "YEARLY")), name="project_task_recurrence"
        ),
    )
    op.create_index("ix_project_tasks_owner_id", "project_tasks", ["owner_id"])
    op.create_index("ix_project_tasks_project_id", "project_tasks", ["project_id"])


def downgrade() -> None:
    op.drop_table("project_tasks")
    op.drop_table("projects")
