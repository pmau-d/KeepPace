"""Checklists des tâches (clientes et de projet)

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "checklist_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("task_id", sa.String(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True),
        sa.Column(
            "project_task_id",
            sa.String(),
            sa.ForeignKey("project_tasks.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "(task_id IS NOT NULL AND project_task_id IS NULL)"
            " OR (task_id IS NULL AND project_task_id IS NOT NULL)",
            name="checklist_item_one_parent",
        ),
    )
    op.create_index("ix_checklist_items_task_id", "checklist_items", ["task_id"])
    op.create_index("ix_checklist_items_project_task_id", "checklist_items", ["project_task_id"])


def downgrade() -> None:
    op.drop_table("checklist_items")
