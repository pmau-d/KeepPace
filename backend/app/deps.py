from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import get_db
from app.security import decode_access_token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        # Accepté aussi en en-tête, pour les scripts et clients d'API.
        scheme, _, credentials = request.headers.get("Authorization", "").partition(" ")
        token = credentials if scheme.lower() == "bearer" else None
    user_id = decode_access_token(token) if token else None
    user = db.get(models.User, user_id) if user_id else None
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise")
    return user
