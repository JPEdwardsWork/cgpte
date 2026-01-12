# US Retail Insights Intelligence Demo

This example demonstrates how to wire multiple data feeds into a lightweight
insights workflow tailored for US retail teams. It combines:

- **Industry press coverage** exported as CSV files
- **Curated trend narratives** captured by analysts
- **Programmatic market signals** delivered through APIs (with an offline sample)
- **Search behaviour monitoring** sourced from consumer intent tools

The pipeline normalises all feeds and publishes an HTML dashboard with
news highlights, curated insights, and charts summarising demand signals.
The sample data is synthetic and refreshed through February 2025 so you can
swap in your own exports without changing the pipeline.

## Running the demo

```bash
python -m examples.us_retail_insights.dashboard --output ./examples/us_retail_insights/output/us_retail_dashboard.html
```

The command produces:

- `output/us_retail_dashboard.html`: the dashboard ready for sharing
- `output/search_trends.png` and `output/market_signals.png`: static charts used by the dashboard

Open the HTML file in a browser to explore the latest aggregated insights.

## Connecting live APIs

The `ExternalMarketSignalClient` class (see `fetchers.py`) is API-ready. Set the
`api_key` parameter when constructing the client to authenticate against your
provider. The dashboard script currently uses a local JSON file when no key is
present so the demo can run offline. Replace `market_signals.json` with the
payload expected from your provider or override `build_default_pipeline` to plug
in a custom client implementation.

## Customising data feeds

Each data connector accepts file paths, making it easy to swap in your own
exports:

- Replace `data/industry_press_articles.csv` with a fresh download from your
  media monitoring tool.
- Update `data/curated_trends.json` with your team's latest narratives.
- Drop a new `data/search_behavior.csv` to refresh the search chart.
- Replace or remove the offline API payload when you connect a live endpoint.

The dashboard will automatically pick up the changes the next time you run the
script.

## Suggested upgrades

- Stream press and trend feeds via webhooks, then store raw payloads for audit
  trails and reprocessing.
- Add topic clustering or summarisation for news coverage to reduce noise in
  the headline list.
- Introduce anomaly detection on search and traffic signals to trigger alerts
  for sudden demand shifts.
- Segment dashboards by region, banner, or category to surface localised
  opportunities.
- Publish dashboards on a schedule with a notification workflow (Slack, email,
  or Teams) when priority thresholds are met.

## Extending the experience

- Wire the pipeline into a scheduler (e.g. GitHub Actions) to publish the
  dashboard daily.
- Enrich the dashboard with geographic segmentation or additional benchmark
  metrics.
- Export the bundle to downstream analytics tools—`RetailInsightsBundle`
  exposes pandas DataFrames suitable for deeper analysis.
