from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://keeppace_user:keeppace_password@db:5432/keeppace_dev"

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
