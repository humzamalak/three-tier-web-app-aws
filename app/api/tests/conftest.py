import os

import pytest
from fastapi.testclient import TestClient

# CI sets DATABASE_URL to a real PostgreSQL service. Locally, SQLite is used.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")


@pytest.fixture
def client():
    from app.db import metadata
    from app.main import app

    with TestClient(app) as c:
        yield c
        metadata.drop_all(app.state.engine)
