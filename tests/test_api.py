from fastapi.testclient import TestClient

from geosite_api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api"}


def test_version_endpoint() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project"] == "geosite-agent"
    assert payload["service"] == "api"
    assert payload["milestone"] == "1-project-skeleton"


def test_sites_demo_endpoint() -> None:
    response = client.get("/sites/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"]
    assert payload["sites"][0]["priority"] == "high"
    assert payload["sites"][0]["agent_report"]["requires_human_review"] is True
