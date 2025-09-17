"""Generate a lightweight HTML dashboard with retail intelligence signals."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from .pipeline import RetailInsightsBundle, build_default_pipeline


def _save_plot(fig: plt.Figure, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _render_search_trend_chart(bundle: RetailInsightsBundle, output_dir: Path) -> Path:
    pivot = bundle.search_trend_pivot()
    fig, ax = plt.subplots(figsize=(8, 4))
    pivot.plot(ax=ax)
    ax.set_title("Organic search interest for key retail intents")
    ax.set_xlabel("Week")
    ax.set_ylabel("Search interest index (0-100)")
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.autofmt_xdate(rotation=30)
    return _save_plot(fig, output_dir / "search_trends.png")


def _render_market_signal_chart(bundle: RetailInsightsBundle, output_dir: Path) -> Path:
    summary = bundle.market_signal_summary()
    latest = summary.groupby(level=0).tail(1)
    latest.index = latest.index.droplevel("date")
    fig, ax = plt.subplots(figsize=(8, 4))
    latest.plot(kind="bar", ax=ax)
    ax.set_title("Latest benchmark metrics by segment")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Indexed performance vs. baseline")
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=20, ha="right")
    return _save_plot(fig, output_dir / "market_signals.png")


def _to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _news_cards(news: pd.DataFrame) -> Iterable[str]:
    for _, row in news.iterrows():
        yield f"""
        <article class='news-card'>
            <h3>{row['headline']}</h3>
            <p class='meta'>{row['date']} · {row['source']} · {row['topic']}</p>
            <p>{row['summary']}</p>
            <a href='{row['url']}' target='_blank'>Read more</a>
        </article>
        """


def _trend_cards(trends: pd.DataFrame) -> Iterable[str]:
    for _, row in trends.iterrows():
        bullets = "".join(f"<li>{item}</li>" for item in row.get("implications", []))
        yield f"""
        <article class='trend-card'>
            <h3>{row['trend']}</h3>
            <p>{row['insight']}</p>
            <ul>{bullets}</ul>
        </article>
        """


def _compose_html(bundle: RetailInsightsBundle, search_chart: Path, market_chart: Path) -> str:
    encoded_search = _to_base64(search_chart)
    encoded_market = _to_base64(market_chart)
    news_html = "".join(_news_cards(bundle.latest_news(limit=6)))
    trends_html = "".join(_trend_cards(bundle.curated_trends))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='utf-8'>
        <title>US Retail Intelligence Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f7fb; color: #1f2933; margin: 0; padding: 2rem; }}
            header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 2rem; }}
            h1 {{ margin: 0; font-size: 2rem; }}
            section {{ margin-bottom: 2rem; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }}
            .news-card, .trend-card {{ background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08); }}
            .news-card a {{ color: #1d4ed8; text-decoration: none; font-weight: 600; }}
            .news-card .meta {{ color: #52606d; font-size: 0.85rem; margin-bottom: 0.5rem; }}
            img.chart {{ width: 100%; border-radius: 12px; box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08); }}
        </style>
    </head>
    <body>
        <header>
            <h1>US Retail Intelligence Dashboard</h1>
            <p>Generated {generated_at}</p>
        </header>
        <section>
            <h2>Fresh from industry press</h2>
            <div class='grid'>
                {news_html}
            </div>
        </section>
        <section>
            <h2>Search behaviour watchlist</h2>
            <img class='chart' src='data:image/png;base64,{encoded_search}' alt='Search trend chart'>
        </section>
        <section>
            <h2>Market signal benchmarks</h2>
            <img class='chart' src='data:image/png;base64,{encoded_market}' alt='Market signal chart'>
        </section>
        <section>
            <h2>Curated trend narratives</h2>
            <div class='grid'>
                {trends_html}
            </div>
        </section>
    </body>
    </html>
    """


def generate_dashboard(output_path: Path, bundle: RetailInsightsBundle) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir = output_path.parent

    search_chart = _render_search_trend_chart(bundle, output_dir)
    market_chart = _render_market_signal_chart(bundle, output_dir)

    html = _compose_html(bundle, search_chart, market_chart)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the US retail intelligence dashboard.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "us_retail_dashboard.html",
        help="Where to save the generated HTML dashboard.",
    )
    return parser.parse_args()


def main() -> Tuple[Path, RetailInsightsBundle]:
    args = parse_args()
    pipeline = build_default_pipeline()
    bundle = pipeline.run()
    output_path = generate_dashboard(args.output, bundle)
    return output_path, bundle


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    path, _ = main()
    print(f"Dashboard generated at {path}")
