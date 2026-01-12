"""Data access helpers for the US retail insights demo platform."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import requests


@dataclass
class IndustryPressFeed:
    """Load industry press coverage from CSV exports."""

    csv_path: Path

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path, parse_dates=["date"])
        if df.empty:
            raise ValueError("Industry press feed is empty; confirm the CSV export.")
        df["date"] = df["date"].dt.date
        return df.sort_values("date", ascending=False).reset_index(drop=True)


@dataclass
class CuratedTrendRepository:
    """Load curated trend summaries from JSON."""

    json_path: Path

    def load(self) -> pd.DataFrame:
        payload = json.loads(self.json_path.read_text())
        if not isinstance(payload, Iterable):
            raise ValueError("Curated trend payload must be an iterable of objects.")
        df = pd.DataFrame(payload)
        if df.empty:
            raise ValueError("Curated trends repository is empty; provide at least one trend.")
        return df


@dataclass
class SearchTrendRepository:
    """Load organic search behaviour metrics."""

    csv_path: Path

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path, parse_dates=["week"])
        if df.empty:
            raise ValueError("Search trend repository is empty; confirm the export.")
        return df


class ExternalMarketSignalClient:
    """Client for metrics delivered via an authenticated API."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        offline_path: Optional[Path] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.offline_path = offline_path
        self.session = session or requests.Session()

    def fetch_metrics(self) -> pd.DataFrame:
        """Fetch market signals.

        If an API key is available we perform an authenticated request. Otherwise we
        fall back to a local JSON file so the example can run offline. The JSON file
        should contain a list of objects with ``date``, ``metric``, ``segment`` and
        ``value`` keys.
        """

        if self.api_key:
            url = f"{self.base_url}/market-signals"
            response = self.session.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=30)
            response.raise_for_status()
            payload = response.json()
        elif self.offline_path:
            payload = json.loads(Path(self.offline_path).read_text())
        else:
            raise ValueError("Either an API key or an offline_path must be provided.")

        df = pd.DataFrame(payload)
        if df.empty:
            raise ValueError("Market signal payload is empty.")
        df["date"] = pd.to_datetime(df["date"])
        return df


__all__ = [
    "IndustryPressFeed",
    "CuratedTrendRepository",
    "SearchTrendRepository",
    "ExternalMarketSignalClient",
]
