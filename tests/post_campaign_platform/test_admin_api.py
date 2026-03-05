from fastapi.testclient import TestClient

from post_campaign_platform.app import app


client = TestClient(app)


def test_admin_page_loads() -> None:
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Post-Campaign Analysis Admin" in response.text


def test_create_client_project_and_stream() -> None:
    create_client = client.post(
        "/admin/clients",
        data={"name": "Acme", "industry": "Retail", "currency": "USD"},
        follow_redirects=False,
    )
    assert create_client.status_code == 303

    clients = client.get("/api/v1/clients").json()
    assert len(clients) >= 1
    created_client = clients[-1]

    create_project = client.post(
        "/admin/projects",
        data={
            "client_id": created_client["client_id"],
            "name": "Q2 Growth",
            "description": "Growth campaign",
        },
        follow_redirects=False,
    )
    assert create_project.status_code == 303

    projects = client.get(f"/api/v1/clients/{created_client['client_id']}/projects").json()
    assert len(projects) >= 1
    created_project = projects[-1]

    create_stream = client.post(
        "/admin/streams",
        data={
            "client_id": created_client["client_id"],
            "project_id": created_project["project_id"],
            "name": "Retail Executive Stream",
            "platforms": "meta,google_ads",
            "kpis": "cpl,roas",
            "cadence": "daily",
        },
        follow_redirects=False,
    )
    assert create_stream.status_code == 303

    streams = client.get(f"/api/v1/projects/{created_project['project_id']}/streams").json()
    assert len(streams) >= 1
    assert streams[-1]["name"] == "Retail Executive Stream"


def test_insight_endpoint_returns_openai_shaped_response() -> None:
    clients = client.get("/api/v1/clients").json()
    assert clients
    created_client = clients[-1]
    projects = client.get(f"/api/v1/clients/{created_client['client_id']}/projects").json()
    assert projects
    created_project = projects[-1]
    streams = client.get(f"/api/v1/projects/{created_project['project_id']}/streams").json()
    assert streams
    created_stream = streams[-1]

    response = client.post(
        "/api/v1/insights",
        json={
            "client_id": created_client["client_id"],
            "project_id": created_project["project_id"],
            "stream_id": created_stream["stream_id"],
            "question": "Why did CPL increase last week?",
            "date_range": "last_7_days",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert "confidence" in payload
    assert isinstance(payload["recommended_actions"], list)
