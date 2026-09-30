from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.repository import get_company, owned

router = APIRouter(prefix="/companies", tags=["companies"])


def _name_taken(db: Session, user: models.User, name: str, exclude_id: str | None = None) -> bool:
    query = owned(db, models.Company, user).filter(models.Company.name == name)
    if exclude_id:
        query = query.filter(models.Company.id != exclude_id)
    return query.first() is not None


@router.get("/", response_model=list[schemas.CompanyRead])
def get_companies(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return owned(db, models.Company, user).order_by(models.Company.name).all()


@router.post("/", response_model=schemas.CompanyRead, status_code=201)
def create_company(
    data: schemas.CompanyCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    if _name_taken(db, user, data.name):
        raise HTTPException(status_code=400, detail="Company already exists")
    company = models.Company(name=data.name, owner_id=user.id)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=schemas.CompanyRead)
def read_company(
    company_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    return get_company(db, company_id, user)


@router.put("/{company_id}", response_model=schemas.CompanyRead)
def update_company(
    company_id: str,
    data: schemas.CompanyCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    company = get_company(db, company_id, user)
    if _name_taken(db, user, data.name, exclude_id=company_id):
        raise HTTPException(status_code=400, detail="Company name already exists")
    company.name = data.name
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    company = get_company(db, company_id, user)
    # Cascade: supprimer clients → tâches → logs
    for client in list(company.clients):
        for task in list(client.tasks):
            db.delete(task)
        db.delete(client)
    db.delete(company)
    db.commit()
