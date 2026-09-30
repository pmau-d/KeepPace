from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[schemas.CompanyRead])
def get_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).order_by(models.Company.name).all()


@router.post("/", response_model=schemas.CompanyRead, status_code=201)
def create_company(data: schemas.CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Company).filter(models.Company.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
    company = models.Company(name=data.name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=schemas.CompanyRead)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=schemas.CompanyRead)
def update_company(company_id: str, data: schemas.CompanyCreate, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    conflict = db.query(models.Company).filter(
        models.Company.name == data.name,
        models.Company.id != company_id,
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Company name already exists")
    company.name = data.name
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    # Cascade: supprimer clients → tâches → logs
    for client in list(company.clients):
        for task in list(client.tasks):
            db.delete(task)
        db.delete(client)
    db.delete(company)
    db.commit()
