"""Tier 2: REST API for a small task list."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.exc import SQLAlchemyError

from app.db import make_engine, metadata, tasks

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("api")


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = make_engine()
    # Demo shortcut: create the table at start-up. Use Alembic migrations in a real service.
    metadata.create_all(app.state.engine)
    yield
    app.state.engine.dispose()


app = FastAPI(title="Three-tier demo API", version=os.environ.get("APP_VERSION", "dev"), lifespan=lifespan)


def _row(r) -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "done": r.done,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@app.get("/api/health")
def health(response: Response):
    """Used by the ALB target group. Fails if the database is not reachable."""
    try:
        with app.state.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        log.error("health check failed: %s", exc)
        response.status_code = 503
        return {"status": "unhealthy", "database": "unreachable"}
    return {"status": "ok", "database": "ok", "version": app.version}


@app.get("/api/tasks")
def list_tasks():
    with app.state.engine.connect() as conn:
        rows = conn.execute(select(tasks).order_by(tasks.c.id)).all()
    return [_row(r) for r in rows]


@app.post("/api/tasks", status_code=201)
def create_task(body: TaskIn):
    with app.state.engine.begin() as conn:
        new_id = conn.execute(insert(tasks).values(title=body.title.strip()).returning(tasks.c.id)).scalar_one()
        row = conn.execute(select(tasks).where(tasks.c.id == new_id)).one()
    return _row(row)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, body: TaskPatch):
    values = body.model_dump(exclude_none=True)
    if not values:
        raise HTTPException(400, "nothing to update")
    with app.state.engine.begin() as conn:
        result = conn.execute(update(tasks).where(tasks.c.id == task_id).values(**values))
        if result.rowcount == 0:
            raise HTTPException(404, "task not found")
        row = conn.execute(select(tasks).where(tasks.c.id == task_id)).one()
    return _row(row)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with app.state.engine.begin() as conn:
        if conn.execute(delete(tasks).where(tasks.c.id == task_id)).rowcount == 0:
            raise HTTPException(404, "task not found")
    return Response(status_code=204)
