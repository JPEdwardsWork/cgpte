from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PlatformName(str, Enum):
    META = "meta"
    GOOGLE_ADS = "google_ads"
    DV360 = "dv360"
    TIKTOK = "tiktok"
    AMAZON_ADS = "amazon_ads"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    GA4 = "ga4"
    CM360 = "cm360"


class Client(BaseModel):
    client_id: str = Field(..., description="Tenant-safe client identifier")
    name: str
    industry: str
    reporting_currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(BaseModel):
    project_id: str
    client_id: str
    name: str
    description: str = ""
    markets: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReportingStream(BaseModel):
    stream_id: str
    client_id: str
    project_id: str
    name: str
    platforms: list[PlatformName] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)
    cadence: str = "daily"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StrategyDocument(BaseModel):
    doc_id: str
    client_id: str
    project_id: Optional[str] = None
    title: str
    body: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InsightRequest(BaseModel):
    client_id: str
    project_id: str
    stream_id: str
    question: str
    date_range: str = "last_30_days"


class InsightResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[str]
    recommended_actions: list[str] = Field(default_factory=list)
