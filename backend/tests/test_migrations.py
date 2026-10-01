"""Les migrations Alembic doivent produire exactement le schéma des modèles,
et savoir reprendre une base créée par l'ancienne version (create_all)."""

import os

import pytest
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from alembic import command
from app.database import Base

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))

LEGACY_SCHEMA = [
    "CREATE TABLE companies (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL UNIQUE)",
    """CREATE TABLE clients (id VARCHAR PRIMARY KEY, company_id VARCHAR NOT NULL REFERENCES companies(id),
       first_name VARCHAR NOT NULL, last_name VARCHAR NOT NULL, email VARCHAR, absence_end_date DATE)""",
    """CREATE TABLE tasks (id VARCHAR PRIMARY KEY, client_id VARCHAR NOT NULL REFERENCES clients(id),
       title VARCHAR NOT NULL, description TEXT, status VARCHAR NOT NULL, priority VARCHAR NOT NULL,
       due_date DATE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    """CREATE TABLE task_logs (id VARCHAR PRIMARY KEY, task_id VARCHAR NOT NULL REFERENCES tasks(id),
       field_changed VARCHAR NOT NULL, old_value TEXT, new_value TEXT, comment TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
]


@pytest.fixture()
def database_url(tmp_path):
    return os.environ.get("MIGRATION_TEST_DATABASE_URL") or f"sqlite:///{tmp_path / 'migrations.db'}"


TABLES = ("task_logs", "task_comments", "tasks", "clients", "companies", "users", "alembic_version")


def _drop_all(engine) -> None:
    with engine.begin() as conn:
        for table in TABLES:
            conn.execute(
                text(
                    f"DROP TABLE IF EXISTS {table} CASCADE"
                    if _is_pg(conn)
                    else f"DROP TABLE IF EXISTS {table}"
                )
            )


@pytest.fixture()
def engine(database_url):
    engine = create_engine(database_url)
    _drop_all(engine)
    yield engine
    # En CI, la base PostgreSQL est partagée avec les autres tests : on ne laisse
    # ni tables ni données (les données « anciennes » seraient sinon rattachées
    # au premier compte créé par le test suivant).
    _drop_all(engine)
    engine.dispose()


def _is_pg(conn) -> bool:
    return conn.dialect.name == "postgresql"


def _upgrade(engine, revision: str = "head") -> None:
    config = Config(os.path.join(BACKEND_DIR, "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def test_migrations_match_models(engine):
    _upgrade(engine)
    with engine.connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    assert diff == []


def test_legacy_database_is_upgraded_without_data_loss(engine):
    with engine.begin() as conn:
        for statement in LEGACY_SCHEMA:
            conn.execute(text(statement))
        conn.execute(text("INSERT INTO companies VALUES ('co', 'Acme'), ('co2', 'Globex')"))
        conn.execute(
            text(
                "INSERT INTO clients VALUES ('cl', 'co', 'Alice', 'Martin', NULL, NULL), "
                "('cl2', 'co2', 'Bob', '', NULL, NULL)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO tasks (id, client_id, title, status, priority) "
                "VALUES ('t1', 'cl', 'Relancer', 'IN_PROGRESS', 'HIGH'), ('t2', 'cl', 'Vieux', 'WEIRD', '??')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO task_logs (id, task_id, field_changed, old_value, new_value) "
                "VALUES ('l1', 't1', 'client_id', 'cl2', 'cl')"
            )
        )

    _upgrade(engine)

    with engine.connect() as conn:
        rows = dict(conn.execute(text("SELECT id, status || '/' || priority FROM tasks")).all())
        assert rows == {"t1": "IN_PROGRESS/HIGH", "t2": "TODO/MEDIUM"}
        columns = {c["name"]: c for c in inspect(conn).get_columns("clients")}
        assert columns["last_name"]["nullable"]
        assert inspect(conn).has_table("task_comments")
        labels = conn.execute(text("SELECT old_label, new_label FROM task_logs WHERE id = 'l1'")).one()
        assert tuple(labels) == ("Bob · Globex", "Alice Martin · Acme")
