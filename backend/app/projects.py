"""Adresse (slug) des projets : stable, sans accents, unique par compte."""

import re
import unicodedata

from sqlalchemy.orm import Session

from app import models


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "projet"


def public_address_taken(db: Session, project: models.Project) -> bool:
    """Un autre projet public (actif) a déjà cette adresse : /projets/<slug> doit rester sans ambiguïté."""
    return (
        db.query(models.Project.id)
        .filter(
            models.Project.slug == project.slug,
            models.Project.id != project.id,
            models.Project.is_public.is_(True),
            models.Project.archived_at.is_(None),
        )
        .first()
        is not None
    )


def unique_slug(db: Session, owner_id: str, name: str) -> str:
    """Le slug du nom, suffixé -2, -3… s'il existe déjà (même pour un projet archivé)."""
    base = slugify(name)
    taken = {
        slug
        for (slug,) in db.query(models.Project.slug).filter(
            models.Project.owner_id == owner_id, models.Project.slug.like(f"{base}%")
        )
    }
    slug, n = base, 1
    while slug in taken:
        n += 1
        slug = f"{base}-{n}"
    return slug
