from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, update
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.security import (
    create_access_token,
    hash_password,
    login_limiter,
    needs_rehash,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Hash factice : même coût de vérification qu'un compte existant, pour ne pas
# révéler par le temps de réponse qu'une adresse est inconnue.
_DUMMY_HASH = hash_password("keeppace-dummy-password")


def _set_session_cookie(response: Response, user: models.User) -> None:
    response.set_cookie(
        settings.COOKIE_NAME,
        create_access_token(user.id),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _adopt_legacy_data(db: Session, user: models.User) -> None:
    """Rattache au tout premier compte les données créées avant l'authentification."""
    for model in (models.Company, models.Client, models.Task):
        db.execute(update(model).where(model.owner_id.is_(None)).values(owner_id=user.id))


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    if not settings.ALLOW_REGISTRATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Les inscriptions sont fermées")
    email = data.email.lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Un compte existe déjà avec cet email"
        )

    is_first_user = db.query(func.count(models.User.id)).scalar() == 0
    user = models.User(email=email, full_name=data.full_name, password_hash=hash_password(data.password))
    db.add(user)
    db.flush()
    if is_first_user:
        _adopt_legacy_data(db, user)
    db.commit()
    db.refresh(user)
    _set_session_cookie(response, user)
    return user


@router.post("/login", response_model=schemas.UserRead)
def login(data: schemas.LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    email = data.email.lower()
    limiter_key = f"{request.client.host if request.client else '?'}:{email}"
    if login_limiter.is_blocked(limiter_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Réessayez dans quelques minutes.",
        )

    user = db.query(models.User).filter(models.User.email == email).first()
    valid = verify_password(user.password_hash if user else _DUMMY_HASH, data.password)
    if not user or not valid or not user.is_active:
        login_limiter.record_failure(limiter_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect"
        )

    login_limiter.reset(limiter_key)
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)
        db.commit()
    _set_session_cookie(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(settings.COOKIE_NAME, path="/", secure=settings.cookie_secure, httponly=True)


@router.get("/me", response_model=schemas.UserRead)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=schemas.UserRead)
def update_me(
    data: schemas.UserUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
