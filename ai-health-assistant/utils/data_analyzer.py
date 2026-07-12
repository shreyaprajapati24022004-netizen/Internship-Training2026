"""
data_analyzer.py
----------------
Handles loading the health CSV data and running Pandas-based
calculations, status checks, and simple correlation analysis.
"""

import pandas as pd
import numpy as np
import os


def load_health_data(path: str = "sample_health_data.csv") -> pd.DataFrame:
    """Load the health CSV into a DataFrame. Returns an empty DataFrame if missing."""
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def get_latest_metrics(df: pd.DataFrame) -> dict:
    """Return the most recent day's metrics as a dictionary."""
    if df.empty:
        return {}
    latest = df.iloc[-1]
    return latest.to_dict()


def get_status(metric_name: str, value: float) -> dict:
    """
    Return a status level (good / warning / bad) and color for a given
    metric + value, used to color-code the dashboard cards.
    """
    thresholds = {
        "steps": {"good": 8000, "warning": 5000},
        "sleep_hours": {"good": 7, "warning": 6},
        "heart_rate": {"good": (60, 80), "warning": (50, 95)},
        "water_intake_l": {"good": 2.5, "warning": 1.5},
        "mood_score": {"good": 7, "warning": 5},
    }

    if metric_name not in thresholds:
        return {"level": "neutral", "color": "#8b93a7"}

    rule = thresholds[metric_name]

    # Heart rate uses a "healthy range" instead of "higher is better"
    if metric_name == "heart_rate":
        good_lo, good_hi = rule["good"]
        warn_lo, warn_hi = rule["warning"]
        if good_lo <= value <= good_hi:
            return {"level": "good", "color": "#2ee6a6"}
        elif warn_lo <= value <= warn_hi:
            return {"level": "warning", "color": "#f5c451"}
        else:
            return {"level": "bad", "color": "#ff5c7a"}

    # Everything else: higher is better
    if value >= rule["good"]:
        return {"level": "good", "color": "#2ee6a6"}
    elif value >= rule["warning"]:
        return {"level": "warning", "color": "#f5c451"}
    else:
        return {"level": "bad", "color": "#ff5c7a"}


def weekly_summary(df: pd.DataFrame) -> dict:
    """Average of the last 7 days vs the previous 7 days, with % change."""
    if df.empty or len(df) < 2:
        return {}

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    last7 = df.tail(7)[numeric_cols].mean()
    prev7 = df.iloc[-14:-7][numeric_cols].mean() if len(df) >= 14 else df.head(len(df) - 7)[numeric_cols].mean()

    summary = {}
    for col in numeric_cols:
        current = last7.get(col, np.nan)
        previous = prev7.get(col, np.nan)
        if previous and not np.isnan(previous) and previous != 0:
            pct_change = ((current - previous) / previous) * 100
        else:
            pct_change = 0.0
        summary[col] = {
            "current_avg": round(current, 2) if not np.isnan(current) else None,
            "pct_change": round(pct_change, 1),
        }
    return summary


def compute_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Return a correlation matrix across numeric health metrics."""
    if df.empty:
        return pd.DataFrame()
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.corr()


def build_context_string(df: pd.DataFrame) -> str:
    """
    Build a short plain-text summary of the user's recent health data.
    This gets passed to the Ollama model so the AI Coach has context
    about the person's real stats.
    """
    if df.empty:
        return "No health data available."

    latest = get_latest_metrics(df)
    summary = weekly_summary(df)

    lines = [
        f"Most recent day ({latest.get('date')}):",
        f"- Steps: {latest.get('steps')}",
        f"- Sleep: {latest.get('sleep_hours')} hours",
        f"- Heart rate: {latest.get('heart_rate')} bpm",
        f"- Calories burned: {latest.get('calories_burned')}",
        f"- Water intake: {latest.get('water_intake_l')} L",
        f"- Mood score (1-10): {latest.get('mood_score')}",
        "",
        "7-day averages (vs previous 7 days):",
    ]
    for metric, stats in summary.items():
        if metric == "date":
            continue
        lines.append(f"- {metric}: avg {stats['current_avg']} ({stats['pct_change']:+.1f}% change)")

    return "\n".join(lines)

def append_entry(path: str, entry: dict):
    """
    Append a single new day's health entry to the CSV.
    Creates the file with headers if it doesn't exist yet.
    Ensures the file ends with a newline before appending so rows
    never get merged onto the same line.
    """
    columns = ["date", "steps", "sleep_hours", "heart_rate",
               "calories_burned", "water_intake_l", "mood_score"]

    file_exists = os.path.exists(path) and os.path.getsize(path) > 0

    if file_exists:
        # Make sure the file ends with a newline before we append
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            if size > 0:
                f.seek(size - 1)
                last_char = f.read(1)
        if last_char != b"\n":
            with open(path, "a", newline="") as f:
                f.write("\n")

    new_row = pd.DataFrame([entry], columns=columns)
    new_row.to_csv(path, mode="a" if file_exists else "w",
                    header=not file_exists, index=False, lineterminator="\n")