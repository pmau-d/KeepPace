from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints, model_validator

from app.enums import PresenceStatus, TaskPriority, TaskStatus

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
OptionalName = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None

# ─── Auth ───────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: OptionalName = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class UserRead(BaseModel):
    id: str
    email: str
    full_name: str | None = None

    model_config = {"from_attributes": True}


# ─── Company ────────────────────────────────────────────────────────────────


class CompanyCreate(BaseModel):
    name: Name


class CompanyRead(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


# ─── Client ─────────────────────────────────────────────────────────────────


class AbsencePeriod(BaseModel):
    absence_start_date: date | None = None
    absence_end_date: date | None = None

    @model_validator(mode="after")
    def _end_after_start(self):
        if (
            self.absence_start_date
            and self.absence_end_date
            and self.absence_end_date < self.absence_start_date
        ):
            raise ValueError("La fin d'absence doit suivre son début")
        return self


class ClientCreate(AbsencePeriod):
    company_id: str
    first_name: Name
    last_name: OptionalName = None  # optionnel — seuls prénom + entreprise sont requis
    email: EmailStr | None = None


class ClientUpdate(AbsencePeriod):
    first_name: Name | None = None
    last_name: OptionalName = None
    email: EmailStr | None = None
    company_id: str | None = None


class ClientRead(BaseModel):
    id: str
    company_id: str
    first_name: str
    last_name: str | None = None
    email: str | None = None
    absence_start_date: date | None = None
    absence_end_date: date | None = None
    company: CompanyRead
    presence_status: PresenceStatus | None = None

    model_config = {"from_attributes": True}


# ─── TaskComment ──────────────────────────────────────────────────────────────


class TaskCommentCreate(BaseModel):
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)]


class TaskCommentRead(BaseModel):
    id: str
    task_id: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── TaskLog ─────────────────────────────────────────────────────────────────


class TaskLogRead(BaseModel):
    id: str
    task_id: str
    field_changed: str
    old_value: str | None = None
    new_value: str | None = None
    old_label: str | None = None
    new_label: str | None = None
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Task ────────────────────────────────────────────────────────────────────


class TaskCreate(BaseModel):
    client_id: str
    title: Name
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    sub_status: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: Name | None = None
    description: str | None = None
    client_id: str | None = None
    status: TaskStatus | None = None
    sub_status: str | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    comment: str | None = None  # stored in log, not in task


class TaskSummary(BaseModel):
    """Représentation allégée pour les listes (sans commentaires ni journal)."""

    id: str
    client_id: str
    title: str
    description: str | None = None
    status: TaskStatus
    sub_status: str | None = None
    priority: TaskPriority
    due_date: date | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    client: ClientRead
    comments_count: int = 0

    model_config = {"from_attributes": True}


class TaskRead(TaskSummary):
    """Détail d'une tâche ; le journal se lit via GET /tasks/{id}/logs."""

    comments: list[TaskCommentRead] = []


class TaskPage(BaseModel):
    items: list[TaskSummary]
    total: int
    limit: int
    offset: int
