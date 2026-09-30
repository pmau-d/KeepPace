from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.repository import get_client, get_company, owned
from app.utils import enrich_client

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=list[schemas.ClientRead])
def get_clients(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return [enrich_client(c) for c in owned(db, models.Client, user).all()]


@router.post("/", response_model=schemas.ClientRead, status_code=201)
def create_client(
    data: schemas.ClientCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    get_company(db, data.company_id, user)
    client = models.Client(**data.model_dump(), owner_id=user.id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return enrich_client(client)


@router.get("/{client_id}", response_model=schemas.ClientRead)
def read_client(client_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return enrich_client(get_client(db, client_id, user))


@router.put("/{client_id}", response_model=schemas.ClientRead)
def update_client(
    client_id: str,
    data: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    client = get_client(db, client_id, user)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("company_id"):
        get_company(db, changes["company_id"], user)
    for field, value in changes.items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return enrich_client(client)


@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    client = get_client(db, client_id, user)
    # Les tâches (et leurs logs) seront supprimées en cascade
    for task in list(client.tasks):
        db.delete(task)
    db.delete(client)
    db.commit()
