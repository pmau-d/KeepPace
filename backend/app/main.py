from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models as db_models  # noqa – registers models with Base
from app.database import get_db, wait_for_db
from app.routers import clients, companies, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Le schéma est géré par Alembic (`alembic upgrade head`), plus au démarrage.
    wait_for_db()
    yield


app = FastAPI(title="KeepPace API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(clients.router)
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to KeepPace API 🚀", "docs": "/docs"}


@app.delete("/admin/reset", status_code=204, tags=["admin"])
def reset_all_data(db: Session = Depends(get_db)):
    """Supprime toutes les données (task_logs → tasks → clients → companies)."""
    db.query(db_models.TaskLog).delete()
    db.query(db_models.Task).delete()
    db.query(db_models.Client).delete()
    db.query(db_models.Company).delete()
    db.commit()
