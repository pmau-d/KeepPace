from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


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
    last_name: Optional[str] = None   # optionnel — seuls prénom + entreprise sont requis
    email: Optional[str] = None
    absence_end_date: Optional[date] = None


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    absence_end_date: Optional[date] = None
    company_id: Optional[str] = None


class ClientRead(BaseModel):
    id: str
    company_id: str
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    absence_end_date: Optional[date] = None
    company: CompanyRead
    presence_status: Optional[str] = None

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
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Task ────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    client_id: str
    title: str
    description: Optional[str] = None
    status: str = "TODO"
    sub_status: Optional[str] = None
    priority: str = "MEDIUM"
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[str] = None
    status: Optional[str] = None
    sub_status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    comment: Optional[str] = None  # stored in log, not in task


class TaskRead(BaseModel):
    id: str
    client_id: str
    title: str
    description: Optional[str] = None
    status: str
    sub_status: Optional[str] = None
    priority: str
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    client: ClientRead
    logs: List[TaskLogRead] = []
    comments: List[TaskCommentRead] = []

    model_config = {"from_attributes": True}

