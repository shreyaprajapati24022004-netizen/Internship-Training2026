"""
charts.py
---------
Generates Plotly charts for the "Fresh Obsidian" theme — a deep ocean
gradient (Obsidian -> Midnight Blue -> Cobalt -> Dark Cyan), with amber
for caution and rose for alert readings.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

BG_COLOR = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(234,244,250,0.06)"
FONT_COLOR = "#EAF4FA"
INK_SOFT = "#7FA0BE"
MIDNIGHT = "#01305A"
COBALT = "#024F86"
CYAN = "#048AC1"
CYAN_BRIGHT = "#21B4E8"
AMBER = "#F0B429"
ROSE = "#FF6B81"
SURFACE = "#011C3B"


def _apply_theme_layout(fig, title=None, height=320):
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Playfair Display, serif", size=17, color=FONT_COLOR),
        ) if title else None,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=INK_SOFT, family="JetBrains Mono, monospace", size=11),
        height=height,
        margin=dict(l=10, r=10, t=45 if title else 15, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.2, font=dict(color=INK_SOFT)),
        xaxis=dict(gridcolor=GRID_COLOR, zeroline=False, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zeroline=False, linecolor=GRID_COLOR),
        hoverlabel=dict(bgcolor=SURFACE, font_family="JetBrains Mono, monospace", font_color=FONT_COLOR),
        transition=dict(duration=400, easing="cubic-in-out"),
    )
    return fig


def steps_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"], y=df["steps"],
        marker=dict(color=CYAN, line=dict(width=0)),
        name="Steps",
        hovertemplate="%{x|%b %d}<br>%{y:,} steps<extra></extra>",
    ))
    fig.add_hline(y=8000, line_dash="dot", line_color=AMBER,
                  annotation_text="Goal: 8,000", annotation_font_color=AMBER)
    return _apply_theme_layout(fig, "Daily Steps")


def sleep_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["sleep_hours"],
        mode="lines+markers",
        line=dict(color=CYAN_BRIGHT, width=2.25, shape="spline"),
        marker=dict(size=6, color=CYAN_BRIGHT),
        fill="tozeroy",
        fillcolor="rgba(4,138,193,0.14)",
        name="Sleep (hrs)",
        hovertemplate="%{x|%b %d}<br>%{y} hrs<extra></extra>",
    ))
    fig.add_hline(y=7, line_dash="dot", line_color=AMBER,
                  annotation_text="Target: 7h", annotation_font_color=AMBER)
    return _apply_theme_layout(fig, "Sleep Duration")


def heart_rate_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["heart_rate"],
        mode="lines+markers",
        line=dict(color=ROSE, width=2.25, shape="spline"),
        marker=dict(size=6, color=ROSE),
        name="Resting HR (bpm)",
        hovertemplate="%{x|%b %d}<br>%{y} bpm<extra></extra>",
    ))
    fig.add_hrect(y0=60, y1=80, fillcolor=CYAN, opacity=0.08, line_width=0,
                  annotation_text="Healthy range", annotation_position="top left",
                  annotation_font_color=CYAN_BRIGHT)
    return _apply_theme_layout(fig, "Resting Heart Rate")


def multi_metric_chart(df: pd.DataFrame):
    """Normalized overlay of steps, sleep, and mood to spot patterns."""
    norm = df.copy()
    for col in ["steps", "sleep_hours", "mood_score"]:
        norm[col + "_norm"] = (norm[col] - norm[col].min()) / (norm[col].max() - norm[col].min() + 1e-9)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=norm["date"], y=norm["steps_norm"], mode="lines",
                              name="Steps (normalized)", line=dict(color=CYAN, width=2)))
    fig.add_trace(go.Scatter(x=norm["date"], y=norm["sleep_hours_norm"], mode="lines",
                              name="Sleep (normalized)", line=dict(color=AMBER, width=2)))
    fig.add_trace(go.Scatter(x=norm["date"], y=norm["mood_score_norm"], mode="lines",
                              name="Mood (normalized)", line=dict(color=ROSE, width=2)))
    return _apply_theme_layout(fig, "Trends Overview (Normalized)", height=350)


def correlation_heatmap(corr_df: pd.DataFrame):
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale=[[0, ROSE], [0.5, SURFACE], [1, CYAN_BRIGHT]],
        zmin=-1, zmax=1,
        aspect="auto",
    )
    fig.update_traces(hovertemplate="%{x} vs %{y}<br>corr: %{z:.2f}<extra></extra>")
    return _apply_theme_layout(fig, "Metric Correlations", height=380)