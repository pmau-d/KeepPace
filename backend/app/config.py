from functools import cached_property
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET_KEY = "dev-insecure-secret-key-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    DATABASE_URL: str = "postgresql+psycopg://keeppace_user:keeppace_password@localhost:5432/keeppace_dev"

    # Authentification
    SECRET_KEY: str = DEV_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    COOKIE_NAME: str = "keeppace_session"
    # None : cookie `Secure` en production uniquement (HTTPS requis).
    COOKIE_SECURE: bool | None = None
    ALLOW_REGISTRATION: bool = True
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # Origines autorisées à appeler l'API depuis un autre domaine, séparées par
    # des virgules. Vide par défaut : le frontend passe par le proxy /api.
    CORS_ORIGINS: str = ""

    # Fuseau horaire servant à déterminer « aujourd'hui » (présence, relances).
    TIMEZONE: str = "Europe/Paris"

    # Récap quotidien par email : désactivé par défaut. Il faut aussi un serveur
    # SMTP (en développement, Mailpit : docker compose, http://localhost:8025).
    DIGEST_ENABLED: bool = False
    DIGEST_HOUR: int = 8
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "KeepPace <noreply@example.com>"
    SMTP_STARTTLS: bool = True
    SMTP_SSL: bool = False
    # Adresse publique de l'application, pour les liens des emails.
    APP_URL: str = "http://localhost:3000"

    # Démo publique : crée le compte de démonstration (données fictives) au
    # démarrage s'il n'existe pas, même en production. Jamais pour de vraies données.
    DEMO_MODE: bool = False

    @model_validator(mode="after")
    def _refuse_insecure_production(self):
        if self.ENVIRONMENT == "production" and (
            self.SECRET_KEY == DEV_SECRET_KEY or len(self.SECRET_KEY) < 32
        ):
            raise ValueError("SECRET_KEY doit être défini (32 caractères minimum) en production.")
        return self

    @property
    def email_enabled(self) -> bool:
        return self.DIGEST_ENABLED and bool(self.SMTP_HOST)

    @property
    def cookie_secure(self) -> bool:
        return self.ENVIRONMENT == "production" if self.COOKIE_SECURE is None else self.COOKIE_SECURE

    @cached_property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def sqlalchemy_url(self) -> str:
        """Force le pilote psycopg 3, y compris pour les anciennes URL `postgresql://`."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = "postgresql://" + url.removeprefix("postgres://")
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
        return url


settings = Settings()
