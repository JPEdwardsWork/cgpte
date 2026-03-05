from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .models import Client, Project, ReportingStream, StrategyDocument


class InMemoryStore:
    """Simple in-memory persistence for reference implementation and local demos."""

    def __init__(self) -> None:
        self.clients: Dict[str, Client] = {}
        self.projects: Dict[str, Project] = {}
        self.streams: Dict[str, ReportingStream] = {}
        self.strategy_docs: Dict[str, StrategyDocument] = {}
        self._project_index: Dict[str, List[str]] = defaultdict(list)
        self._stream_index: Dict[str, List[str]] = defaultdict(list)

    def add_client(self, client: Client) -> Client:
        self.clients[client.client_id] = client
        return client

    def add_project(self, project: Project) -> Project:
        self.projects[project.project_id] = project
        self._project_index[project.client_id].append(project.project_id)
        return project

    def add_stream(self, stream: ReportingStream) -> ReportingStream:
        self.streams[stream.stream_id] = stream
        self._stream_index[stream.project_id].append(stream.stream_id)
        return stream

    def add_strategy_doc(self, doc: StrategyDocument) -> StrategyDocument:
        self.strategy_docs[doc.doc_id] = doc
        return doc

    def list_clients(self) -> list[Client]:
        return list(self.clients.values())

    def list_projects(self, client_id: str) -> list[Project]:
        return [self.projects[p] for p in self._project_index.get(client_id, [])]

    def list_streams(self, project_id: str) -> list[ReportingStream]:
        return [self.streams[s] for s in self._stream_index.get(project_id, [])]

    def list_strategy_docs(self, client_id: str) -> list[StrategyDocument]:
        return [doc for doc in self.strategy_docs.values() if doc.client_id == client_id]
