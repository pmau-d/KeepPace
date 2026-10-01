from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.digest import build_digest, render_email, send_email

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/", response_model=schemas.Digest)
def read_digest(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Récap du jour : tâches à relancer, clients qui partent ou reviennent bientôt."""
    return build_digest(db, user)


@router.post("/send", status_code=202)
def send_now(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Envoie le récap du jour à son propre email (pour vérifier la configuration)."""
    if not settings.email_enabled:
        raise HTTPException(status_code=409, detail="L'envoi d'emails n'est pas configuré sur ce serveur")
    try:
        send_email(render_email(user, build_digest(db, user)))
    except OSError as error:
        raise HTTPException(status_code=502, detail="Le serveur d'emails n'a pas accepté l'envoi") from error
    return {"sent_to": user.email}
