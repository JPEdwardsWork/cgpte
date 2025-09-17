from pathlib import Path

import pandas as pd

from examples.us_retail_insights.pipeline import build_default_pipeline


def test_pipeline_produces_non_empty_bundle(tmp_path: Path) -> None:
    pipeline = build_default_pipeline()
    bundle = pipeline.run()

    assert not bundle.news.empty
    assert not bundle.curated_trends.empty
    assert not bundle.search_trends.empty
    assert not bundle.market_signals.empty

    pivot = bundle.search_trend_pivot()
    assert isinstance(pivot, pd.DataFrame)
    assert set(pivot.columns) == {"discount grocery", "curbside pickup", "experience store"}

    summary = bundle.market_signal_summary()
    assert "Apparel" in summary.columns
    assert "Beauty" in summary.columns


def test_dashboard_generation(tmp_path: Path) -> None:
    pipeline = build_default_pipeline()
    bundle = pipeline.run()

    output_path = tmp_path / "dashboard.html"

    from examples.us_retail_insights.dashboard import generate_dashboard

    path = generate_dashboard(output_path, bundle)
    assert path.exists()

    html = path.read_text()
    assert "US Retail Intelligence Dashboard" in html
    assert "Search behaviour watchlist" in html
