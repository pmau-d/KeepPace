from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import models  # noqa: F401 — enregistre les modèles dans Base.metadata
from app.config import settings
from app.database import engine, wait_for_db
from app.digest import start_scheduler
from app.routers import auth, clients, companies, digest, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Le schéma est géré par Alembic (`alembic upgrade head`), plus au démarrage.
    wait_for_db()
    stop_digest = start_scheduler()
    yield
    if stop_digest:
        stop_digest.set()


app = FastAPI(
    title="KeepPace API",
    version="1.1.0",
    lifespan=lifespan,
    # Documentation interactive désactivée en production.
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None,
    openapi_url=None if settings.ENVIRONMENT == "production" else "/openapi.json",
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(auth.router)
app.include_router(digest.router)
app.include_router(companies.router)
app.include_router(clients.router)
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"name": "KeepPace API", "version": app.version}


@app.get("/health", tags=["monitoring"])
def health():
    """Sonde de disponibilité : l'API répond et la base de données aussi."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ok"}
