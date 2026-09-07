from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_lists_categories():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert "invoice" in body["categories"]


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_classify_endpoint():
    resp = client.post(
        "/classify",
        json={"text": "Invoice due on receipt, total amount due: $200."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] == "invoice"
    assert body["destination"] == "queue://finance/accounts-payable"
