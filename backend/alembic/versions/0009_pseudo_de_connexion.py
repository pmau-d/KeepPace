"""Pseudo de connexion ; l'email devient facultatif

Les comptes existants reçoivent un pseudo tiré de leur email (« alice » pour
alice@example.com, suffixé 2, 3… en cas de doublon) et peuvent toujours se
connecter avec leur email.

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-29
"""

import re
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _username_from(email: str) -> str:
    base = re.sub(r"[^a-z0-9._-]+", "", email.split("@")[0].lower())[:28]
    return base.ljust(3, "0")


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("username", sa.String(length=32), nullable=True))

    conn = op.get_bind()
    taken: set[str] = set()
    for user_id, email in conn.execute(sa.text("SELECT id, email FROM users ORDER BY created_at, id")).all():
        base = _username_from(email)
        name, n = base, 1
        while name in taken:
            n += 1
            name = f"{base}{n}"
        taken.add(name)
        conn.execute(
            sa.text("UPDATE users SET username = :name WHERE id = :id"), {"name": name, "id": user_id}
        )

    with op.batch_alter_table("users") as batch:
        batch.alter_column("username", existing_type=sa.String(length=32), nullable=False)
        batch.alter_column("email", existing_type=sa.String(length=320), nullable=True)
        batch.create_unique_constraint("users_username_key", ["username"])


def downgrade() -> None:
    # L'email redevient obligatoire : les comptes sans email en reçoivent un fictif.
    op.execute("UPDATE users SET email = username || '@invalid.local' WHERE email IS NULL")
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("users_username_key", type_="unique")
        batch.alter_column("email", existing_type=sa.String(length=320), nullable=False)
        batch.drop_column("username")
