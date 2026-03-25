"""Live TinyTroupe dashboard inspired by the Crucix-style command center UI.

Run:
    streamlit run examples/live_dashboard.py

Optional event stream input:
    streamlit run examples/live_dashboard.py -- --events path/to/events.jsonl

JSONL schema (one object per line):
    {
      "timestamp": "2026-03-25T15:00:00Z",
      "agent": "Lisa",
      "event_type": "message",
      "sentiment": 0.2,
      "latency_ms": 480,
      "cost_usd": 0.0031,
      "message": "I liked ad B more than ad A."
    }
"""

from __future__ import annotations

import argparse
import json
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

try:
    import streamlit as st
except ImportError as exc:  # pragma: no cover - direct UX feedback only
    raise SystemExit(
        "Streamlit is required for the live dashboard. Install with: pip install streamlit"
    ) from exc


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--events", type=str, default="")
    known, _ = parser.parse_known_args()
    return known


def _load_events(path: str) -> pd.DataFrame:
    if not path:
        return _mock_events()

    event_path = Path(path)
    if not event_path.exists():
        st.warning(f"Events file not found at: {event_path}. Showing synthetic live data.")
        return _mock_events()

    rows: list[dict] = []
    with event_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    if not rows:
        st.warning("Events file is empty. Showing synthetic live data.")
        return _mock_events()

    return _normalize(pd.DataFrame(rows))


def _mock_events(size: int = 220) -> pd.DataFrame:
    now = datetime.now(tz=timezone.utc)
    agents = ["Lisa", "Marcos", "Oscar", "Sophie", "Lila", "Friedrich"]
    event_types = ["message", "evaluation", "observation", "decision"]

    rows: list[dict] = []
    for i in range(size):
        ts = now - timedelta(seconds=(size - i) * random.randint(10, 30))
        rows.append(
            {
                "timestamp": ts.isoformat(),
                "agent": random.choice(agents),
                "event_type": random.choice(event_types),
                "sentiment": round(random.uniform(-1, 1), 3),
                "latency_ms": random.randint(250, 2200),
                "cost_usd": round(random.uniform(0.0008, 0.015), 4),
                "message": random.choice(
                    [
                        "Strong preference for concept B.",
                        "Need more social proof in ad copy.",
                        "Price sensitivity is a concern.",
                        "Feature set appears differentiated.",
                        "Tone sounds too technical for beginners.",
                    ]
                ),
            }
        )

    return _normalize(pd.DataFrame(rows))


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

    defaults = {
        "agent": "Unknown",
        "event_type": "message",
        "sentiment": 0.0,
        "latency_ms": 0.0,
        "cost_usd": 0.0,
        "message": "",
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
    return df


def _render(df: pd.DataFrame) -> None:
    st.set_page_config(page_title="TinyTroupe Live Dashboard", layout="wide")

    st.markdown(
        """
        <style>
            .stApp {background: radial-gradient(circle at top left, #12142a, #0a0b14 45%); color: #f7f8ff;}
            .stMetric {background: rgba(255,255,255,0.03); padding: 10px; border-radius: 12px; border: 1px solid rgba(0,250,255,0.2);}
            div[data-testid="stSidebar"] {background: #101225;}
            .panel {padding: 0.85rem; border-radius: 12px; border: 1px solid rgba(122, 247, 255, 0.35); background: rgba(11,14,28,0.6);}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("⚡ TinyTroupe Live Mission Dashboard")
    st.caption("Crucix-inspired command-center layout for real-time simulation monitoring.")

    left, right = st.columns([1, 2])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("System health")
        st.metric("Events tracked", f"{len(df):,}")
        st.metric("Mean latency", f"{df['latency_ms'].mean():.0f} ms")
        st.metric("Total cost", f"${df['cost_usd'].sum():.2f}")
        st.metric("Avg sentiment", f"{df['sentiment'].mean():+.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Activity over time")
        chart_df = (
            df.set_index("timestamp")
            .resample("5min")
            .size()
            .rename("events")
            .reset_index()
        )
        st.line_chart(chart_df, x="timestamp", y="events", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    bottom_left, bottom_mid, bottom_right = st.columns(3)

    with bottom_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Event mix")
        st.bar_chart(df["event_type"].value_counts(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_mid:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Top active agents")
        st.bar_chart(df["agent"].value_counts().head(8), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Recent feed")
        preview = df[["timestamp", "agent", "event_type", "sentiment", "message"]].tail(12)
        preview["timestamp"] = preview["timestamp"].dt.strftime("%H:%M:%S")
        st.dataframe(preview, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    args = _parse_args()

    with st.sidebar:
        st.header("Dashboard controls")
        auto_refresh = st.toggle("Auto refresh", value=True)
        refresh_seconds = st.slider("Refresh interval (sec)", min_value=2, max_value=30, value=5)
        st.caption("Use --events path/to/events.jsonl to monitor a real run.")

    df = _load_events(args.events)
    _render(df)

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()


if __name__ == "__main__":
    main()
