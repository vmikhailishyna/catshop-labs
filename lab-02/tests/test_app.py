import importlib

import pytest

import app as app_module

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("COUNTER_FILE", str(tmp_path / "visits.txt"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_health_is_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.data.decode().strip() == "ok"


def test_ready_reports_the_file_store_when_there_is_no_database(client):
    body = client.get("/ready").get_json()
    assert body["ready"] is True
    assert body["store"].startswith("file:")


def test_visits_counts_up(client):
    first = client.get("/visits").get_json()["visits"]
    second = client.get("/visits").get_json()["visits"]
    assert second == first + 1

def test_ready_is_503_when_the_database_is_unreachable(tmp_path, monkeypatch):
    monkeypatch.setenv("COUNTER_FILE", str(tmp_path / "visits.txt"))
    monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@127.0.0.1:1/x")
    importlib.reload(app_module)
    r = app_module.app.test_client().get("/ready")
    assert r.status_code == 503
    assert r.get_json()["ready"] is False

def test_price_fails_loudly_when_the_partner_is_unreachable(client, monkeypatch):
    monkeypatch.setenv("PARTNER_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("PARTNER_TIMEOUT", "0.25")
    importlib.reload(app_module)
    r = app_module.app.test_client().get("/price/MK-II")
    assert r.status_code == 502
    body = r.get_json()
    assert body["sku"] == "MK-II"
    assert "127.0.0.1:9" in body["source"]
