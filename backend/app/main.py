from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 — enregistre les modèles dans Base.metadata
from app.config import settings
from app.database import wait_for_db
from app.routers import auth, clients, companies, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Le schéma est géré par Alembic (`alembic upgrade head`), plus au démarrage.
    wait_for_db()
    yield


app = FastAPI(title="KeepPace API", version="1.0.0", lifespan=lifespan)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(clients.router)
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to KeepPace API 🚀", "docs": "/docs"}
