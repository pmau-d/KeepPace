import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)

    clients = relationship("Client", back_populates="company")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)   # optionnel
    email = Column(String, nullable=True)
    absence_end_date = Column(Date, nullable=True)

    company = relationship("Company", back_populates="clients")
    tasks = relationship("Task", back_populates="client")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="TODO")
    sub_status = Column(String, nullable=True)   # statut personnalisé libre
    priority = Column(String, nullable=False, default="MEDIUM")
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="tasks")
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan", order_by="TaskLog.created_at")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan", order_by="TaskComment.created_at")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(String, primary_key=True, default=gen_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="comments")


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    field_changed = Column(String, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="logs")

