from datetime import date, datetime

from pydantic import BaseModel

from app.enums import TaskPriority, TaskStatus

# ─── Company ────────────────────────────────────────────────────────────────


class CompanyCreate(BaseModel):
    name: str


class CompanyRead(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


# ─── Client ─────────────────────────────────────────────────────────────────


class ClientCreate(BaseModel):
    company_id: str
    first_name: str
    last_name: str | None = None  # optionnel — seuls prénom + entreprise sont requis
    email: str | None = None
    absence_end_date: date | None = None


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
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
    content: str


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
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    sub_status: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
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
