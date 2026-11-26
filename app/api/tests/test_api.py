def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["database"] == "ok"


def test_task_lifecycle(client):
    assert client.get("/api/tasks").json() == []

    created = client.post("/api/tasks", json={"title": "  Write README  "})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Write README"
    assert task["done"] is False

    patched = client.patch(f"/api/tasks/{task['id']}", json={"done": True})
    assert patched.json()["done"] is True

    assert [t["id"] for t in client.get("/api/tasks").json()] == [task["id"]]

    assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert client.get("/api/tasks").json() == []


def test_validation(client):
    assert client.post("/api/tasks", json={"title": ""}).status_code == 422
    assert client.post("/api/tasks", json={"title": "x" * 201}).status_code == 422
    assert client.patch("/api/tasks/1", json={}).status_code == 400


def test_missing_task_is_404(client):
    assert client.patch("/api/tasks/999", json={"done": True}).status_code == 404
    assert client.delete("/api/tasks/999").status_code == 404


def test_health_reports_database_down(client):
    from sqlalchemy.exc import OperationalError

    from app.main import app

    class Broken:
        def connect(self):
            raise OperationalError("SELECT 1", {}, Exception("down"))

    real = app.state.engine
    app.state.engine = Broken()
    try:
        r = client.get("/api/health")
    finally:
        app.state.engine = real
    assert r.status_code == 503
    assert r.json()["database"] == "unreachable"
