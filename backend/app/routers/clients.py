from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils import enrich_client

router = APIRouter(prefix="/clients", tags=["clients"])



@router.get("/", response_model=list[schemas.ClientRead])
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(models.Client).all()
    return [enrich_client(c) for c in clients]


@router.post("/", response_model=schemas.ClientRead, status_code=201)
def create_client(data: schemas.ClientCreate, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    client = models.Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return enrich_client(client)


@router.get("/{client_id}", response_model=schemas.ClientRead)
def get_client(client_id: str, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return enrich_client(client)


@router.put("/{client_id}", response_model=schemas.ClientRead)
def update_client(client_id: str, data: schemas.ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return enrich_client(client)


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: str, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # Les tâches (et leurs logs) seront supprimées en cascade
    for task in list(client.tasks):
        db.delete(task)
    db.delete(client)
    db.commit()
