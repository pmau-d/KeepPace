"""Date de début d'absence des clients

Sans date de début, un client dont l'absence ne commence que la semaine
prochaine apparaissait « Absent » dès aujourd'hui.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("clients") as batch:
        batch.add_column(sa.Column("absence_start_date", sa.Date(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("clients") as batch:
        batch.drop_column("absence_start_date")
