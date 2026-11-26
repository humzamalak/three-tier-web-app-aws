"""Database setup. Reads DATABASE_URL, or builds it from DB_* variables.

On ECS the password comes from the RDS-managed secret in Secrets Manager,
injected by the task definition as DB_PASSWORD. It is never in the image.
"""

from __future__ import annotations

import os
from urllib.parse import quote_plus

from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, Table, create_engine, false, func
from sqlalchemy.engine import Engine

metadata = MetaData()

tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("done", Boolean, nullable=False, server_default=false()),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


def database_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    user = quote_plus(os.environ.get("DB_USER", "app"))
    password = quote_plus(os.environ.get("DB_PASSWORD", ""))
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "app")
    sslmode = os.environ.get("DB_SSLMODE", "prefer")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}"


def make_engine(url: str | None = None) -> Engine:
    url = url or database_url()
    kwargs = {"pool_pre_ping": True}
    if not url.startswith("sqlite"):
        kwargs.update(pool_size=5, max_overflow=5, pool_recycle=1800)
    return create_engine(url, **kwargs)
