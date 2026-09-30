import uuid

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import TaskPriority, TaskStatus
from app.types import UTCDateTime, utcnow


def gen_uuid():
    return str(uuid.uuid4())


def _enum(enum_cls, name: str) -> Enum:
    # VARCHAR + contrainte CHECK plutôt qu'un type ENUM natif : portable (SQLite
    # en test) et ajout de valeurs sans migration de type PostgreSQL.
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=20,
        values_callable=lambda e: [m.value for m in e],
        validate_strings=True,
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="users_email_key"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String(320), nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(UTCDateTime, nullable=False, default=utcnow, server_default=func.now())


def _owner_column():
    # Nullable uniquement pour les données antérieures aux comptes : elles sont
    # rattachées au premier compte créé. L'API renseigne toujours ce champ.
    return Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_companies_owner_name"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = _owner_column()
    name = Column(String, nullable=False)

    clients = relationship("Client", back_populates="company")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = _owner_column()
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)  # optionnel
    email = Column(String, nullable=True)
    absence_end_date = Column(Date, nullable=True)

    company = relationship("Company", back_populates="clients")
    tasks = relationship("Task", back_populates="client")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = _owner_column()
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(_enum(TaskStatus, "task_status"), nullable=False, default=TaskStatus.TODO)
    sub_status = Column(String, nullable=True)  # statut personnalisé libre
    priority = Column(_enum(TaskPriority, "task_priority"), nullable=False, default=TaskPriority.MEDIUM)
    due_date = Column(Date, nullable=True)
    created_at = Column(UTCDateTime, nullable=False, default=utcnow, server_default=func.now())
    updated_at = Column(
        UTCDateTime, nullable=False, default=utcnow, server_default=func.now(), onupdate=utcnow
    )

    client = relationship("Client", back_populates="tasks")
    logs = relationship(
        "TaskLog", back_populates="task", cascade="all, delete-orphan", order_by="TaskLog.created_at"
    )
    comments = relationship(
        "TaskComment", back_populates="task", cascade="all, delete-orphan", order_by="TaskComment.created_at"
    )


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(String, primary_key=True, default=gen_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(UTCDateTime, nullable=False, default=utcnow, server_default=func.now())

    task = relationship("Task", back_populates="comments")


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    field_changed = Column(String, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(UTCDateTime, nullable=False, default=utcnow, server_default=func.now())

    task = relationship("Task", back_populates="logs")
