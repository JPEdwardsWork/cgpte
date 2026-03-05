from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import (
    Client,
    InsightRequest,
    PlatformName,
    Project,
    ReportingStream,
    StrategyDocument,
)
from .openai_orchestrator import OpenAIOrchestrator
from .store import InMemoryStore

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Post Campaign Analysis Platform", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

store = InMemoryStore()
orchestrator = OpenAIOrchestrator()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request) -> HTMLResponse:
    clients = store.list_clients()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "clients": clients,
            "platforms": [p.value for p in PlatformName],
        },
    )


@app.post("/admin/clients")
def create_client(name: str = Form(...), industry: str = Form(...), currency: str = Form("USD")):
    client = Client(client_id=f"cl_{uuid4().hex[:8]}", name=name, industry=industry, reporting_currency=currency)
    store.add_client(client)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/projects")
def create_project(client_id: str = Form(...), name: str = Form(...), description: str = Form("")):
    if client_id not in store.clients:
        raise HTTPException(status_code=404, detail="Client not found")

    project = Project(
        project_id=f"prj_{uuid4().hex[:8]}",
        client_id=client_id,
        name=name,
        description=description,
    )
    store.add_project(project)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/streams")
def create_stream(
    client_id: str = Form(...),
    project_id: str = Form(...),
    name: str = Form(...),
    platforms: str = Form(""),
    kpis: str = Form(""),
    cadence: str = Form("daily"),
):
    if client_id not in store.clients:
        raise HTTPException(status_code=404, detail="Client not found")
    if project_id not in store.projects:
        raise HTTPException(status_code=404, detail="Project not found")

    platform_values = [
        PlatformName(p.strip()) for p in platforms.split(",") if p.strip()
    ]
    stream = ReportingStream(
        stream_id=f"str_{uuid4().hex[:8]}",
        client_id=client_id,
        project_id=project_id,
        name=name,
        platforms=platform_values,
        kpis=[k.strip() for k in kpis.split(",") if k.strip()],
        cadence=cadence,
    )
    store.add_stream(stream)
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/api/v1/clients")
def list_clients() -> list[Client]:
    return store.list_clients()


@app.get("/api/v1/clients/{client_id}/projects")
def list_projects(client_id: str) -> list[Project]:
    return store.list_projects(client_id)


@app.get("/api/v1/projects/{project_id}/streams")
def list_streams(project_id: str) -> list[ReportingStream]:
    return store.list_streams(project_id)


@app.post("/api/v1/strategy-documents")
def create_strategy_doc(payload: StrategyDocument) -> StrategyDocument:
    return store.add_strategy_doc(payload)


@app.post("/api/v1/insights")
def create_insight(payload: InsightRequest):
    stream = store.streams.get(payload.stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Reporting stream not found")

    docs = store.list_strategy_docs(payload.client_id)
    return orchestrator.generate_insight(payload, stream, docs)
