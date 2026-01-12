"""Orchestration logic for the US retail insights platform demo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd

from .fetchers import (
    CuratedTrendRepository,
    ExternalMarketSignalClient,
    IndustryPressFeed,
    SearchTrendRepository,
)


@dataclass
class RetailInsightsBundle:
    """Container with all content required by the dashboard."""

    news: pd.DataFrame
    curated_trends: pd.DataFrame
    search_trends: pd.DataFrame
    market_signals: pd.DataFrame

    def latest_news(self, limit: int = 5) -> pd.DataFrame:
        return self.news.head(limit)

    def search_trend_pivot(self) -> pd.DataFrame:
        pivot = self.search_trends.pivot_table(
            index="week", columns="keyword", values="search_index", aggfunc="mean"
        )
        return pivot.sort_index()

    def market_signal_summary(self) -> pd.DataFrame:
        summary = (
            self.market_signals.copy()
            .assign(date=lambda df: df["date"].dt.date)
            .pivot_table(index=["metric", "date"], columns="segment", values="value")
        )
        return summary.sort_index()


class RetailInsightsPipeline:
    """Coordinates data ingestion from the configured sources."""

    def __init__(
        self,
        press_feed: IndustryPressFeed,
        curated_repo: CuratedTrendRepository,
        search_repo: SearchTrendRepository,
        market_client: ExternalMarketSignalClient,
    ) -> None:
        self.press_feed = press_feed
        self.curated_repo = curated_repo
        self.search_repo = search_repo
        self.market_client = market_client

    def run(self) -> RetailInsightsBundle:
        news = self.press_feed.load()
        curated = self.curated_repo.load()
        search = self.search_repo.load()
        market = self.market_client.fetch_metrics()

        return RetailInsightsBundle(
            news=news,
            curated_trends=curated,
            search_trends=search,
            market_signals=market,
        )


def build_default_pipeline(base_path: Path | None = None) -> RetailInsightsPipeline:
    """Helper to create a ready-to-run pipeline bound to local demo assets."""

    root = Path(base_path) if base_path else Path(__file__).resolve().parent
    data_dir = root / "data"

    press_feed = IndustryPressFeed(csv_path=data_dir / "industry_press_articles.csv")
    curated_repo = CuratedTrendRepository(json_path=data_dir / "curated_trends.json")
    search_repo = SearchTrendRepository(csv_path=data_dir / "search_behavior.csv")
    market_client = ExternalMarketSignalClient(
        base_url="https://api.example.com/retail",
        api_key=None,
        offline_path=data_dir / "market_signals.json",
    )

    return RetailInsightsPipeline(
        press_feed=press_feed,
        curated_repo=curated_repo,
        search_repo=search_repo,
        market_client=market_client,
    )


__all__: Dict[str, object] = {
    "RetailInsightsBundle": RetailInsightsBundle,
    "RetailInsightsPipeline": RetailInsightsPipeline,
    "build_default_pipeline": build_default_pipeline,
}
