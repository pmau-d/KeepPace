from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://keeppace_user:keeppace_password@db:5432/keeppace_dev"

    class Config:
        env_file = ".env"


settings = Settings()

