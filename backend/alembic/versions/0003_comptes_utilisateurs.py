"""Comptes utilisateurs et rattachement des données à leur propriétaire

- table users ;
- owner_id sur companies, clients et tasks (nullable : les lignes
  existantes seront rattachées au premier compte créé) ;
- le nom d'entreprise devient unique par propriétaire, et non plus
  globalement.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OWNED_TABLES = ("companies", "clients", "tasks")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="users_email_key"),
    )
    for table in OWNED_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("owner_id", sa.String(), nullable=True))
            batch.create_foreign_key(
                f"{table}_owner_id_fkey", "users", ["owner_id"], ["id"], ondelete="CASCADE"
            )
            batch.create_index(f"ix_{table}_owner_id", ["owner_id"])

    _replace_global_company_name_unique()


def _replace_global_company_name_unique() -> None:
    inspector = sa.inspect(op.get_bind())
    existing = next(
        (uq for uq in inspector.get_unique_constraints("companies") if uq["column_names"] == ["name"]), None
    )
    # Une ancienne base SQLite porte une contrainte UNIQUE anonyme : on lui donne
    # un nom par convention pour pouvoir la supprimer en mode batch.
    convention = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
    with op.batch_alter_table("companies", naming_convention=convention) as batch:
        if existing is not None:
            batch.drop_constraint(existing["name"] or "uq_companies_name", type_="unique")
        batch.create_unique_constraint("uq_companies_owner_name", ["owner_id", "name"])


def downgrade() -> None:
    with op.batch_alter_table("companies") as batch:
        batch.drop_constraint("uq_companies_owner_name", type_="unique")
        batch.create_unique_constraint("companies_name_key", ["name"])
    for table in OWNED_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.drop_index(f"ix_{table}_owner_id")
            batch.drop_constraint(f"{table}_owner_id_fkey", type_="foreignkey")
            batch.drop_column("owner_id")
    op.drop_table("users")
