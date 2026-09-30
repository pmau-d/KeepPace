from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import wait_for_db, engine, Base, get_db
from sqlalchemy import text
from app.routers import companies, clients, tasks
from app import models as db_models  # noqa – registers models with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    # Migrations idempotentes
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE clients ALTER COLUMN last_name DROP NOT NULL"))
            conn.commit()
    except Exception:
        pass
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS sub_status VARCHAR"))
            conn.commit()
    except Exception:
        pass
    print("✅ All tables created / verified.")
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


