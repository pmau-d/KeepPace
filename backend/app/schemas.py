from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from app.enums import TaskPriority, TaskStatus

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


class ClientCreate(BaseModel):
    company_id: str
    first_name: Name
    last_name: OptionalName = None  # optionnel — seuls prénom + entreprise sont requis
    email: EmailStr | None = None
    absence_end_date: date | None = None


class ClientUpdate(BaseModel):
    first_name: Name | None = None
    last_name: OptionalName = None
    email: EmailStr | None = None
    absence_end_date: date | None = None
    company_id: str | None = None


class ClientRead(BaseModel):
    id: str
    company_id: str
    first_name: str
    last_name: str | None = None
    email: str | None = None
    absence_end_date: date | None = None
    company: CompanyRead
    presence_status: str | None = None

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


class TaskRead(BaseModel):
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
    client: ClientRead
    logs: list[TaskLogRead] = []
    comments: list[TaskCommentRead] = []

    model_config = {"from_attributes": True}
