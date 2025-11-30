# history/charts/rates/policy_rates/line_regime.py

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def render(df, title):
    """
    Line chart with regime shading (Hiking / Easing).
    Features:
    - clean white line
    - red/green shading
    - dashed horizontal gridlines (custom)
    - dashed vertical lines every 4 years
    - custom hover with regime color text
    """

    # -------------------------
    # CLEAN + SORT
    # -------------------------
    df = df.dropna(subset=["value"])
    df = df.sort_values("date")

    # -------------------------
    # PREPARE REGIME LABELS
    # -------------------------
    def color_regime(r):
        if r == "Hiking":
            return "<span style='color:#ff0000;'><b>Hiking</b></span>"
        if r == "Easing":
            return "<span style='color:#00CC00;'><b>Easing</b></span>"
        return ""

    if "regime" not in df.columns:
        raise ValueError("line_regime chart requires a 'regime' column in SQL output.")

    df["regime_color"] = df["regime"].apply(color_regime)

    # -------------------------
    # INIT FIGURE
    # -------------------------
    fig = go.Figure()

    # -------------------------
    # MAIN LINE
    # -------------------------
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["value"],
        mode="lines",
        customdata=df["regime_color"],
        line=dict(width=1.8, color="white"),
        hovertemplate="%{y:.2f}%<br><b>%{customdata}</b><extra></extra>",
        showlegend=False
    ))

    # -------------------------
    # BUILD SHADING (REGIME BLOCKS)
    # -------------------------
    regimes = df["regime"].fillna("NO").tolist()
    dates = df["date"].tolist()

    blocks = []
    start = None
    current = None

    for i, r in enumerate(regimes):
        if r != "NO":
            if current is None:
                start = dates[i]
                current = r
            elif r != current:
                blocks.append((start, dates[i], current))
                start = dates[i]
                current = r
        else:
            if current is not None:
                blocks.append((start, dates[i], current))
                current = None

    # close last block
    if current is not None:
        blocks.append((start, dates[-1], current))

    COLORS = {
        "Hiking": "rgba(255, 155, 155, 0.8)",
        "Easing": "rgba(150, 255, 150, 0.8)",
    }

    for (x0, x1, reg) in blocks:
        fig.add_vrect(
            x0=x0,
            x1=x1,
            fillcolor=COLORS.get(reg, "rgba(255,255,255,0.1)"),
            opacity=0.8,
            line_width=0,
            layer="below",
        )

    # -------------------------
    # CUSTOM GRIDLINES
    # -------------------------
    y_min = df["value"].min()
    y_max = df["value"].max()

    # Horizontal (every 1 unit)
    y_ticks = np.arange(np.floor(y_min), np.ceil(y_max) + 0.1, 1)

    for y in y_ticks:
        fig.add_shape(
            type="line",
            x0=df["date"].min(),
            x1=df["date"].max(),
            y0=y, y1=y,
            line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dot"),
            layer="below"
        )

    # Vertical (every 4 years)
    years = df["date"].dt.year.unique()
    for year in years:
        if year % 4 == 0:
            fig.add_shape(
                type="line",
                x0=f"{year}-01-01",
                x1=f"{year}-01-01",
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dot"),
                layer="below"
            )

    # -------------------------
    # LAYOUT
    # -------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(family="Courier Prime", color="white"),

        margin=dict(l=40, r=40, t=10, b=10),
        height=250,
        hovermode="x",

        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font=dict(
                family="Courier Prime",
                color="black",
                size=13
            ),
        ),

        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            dtick="M48",
            tickfont=dict(color="white"),
            hoverformat="%d %b %Y",
        ),

        yaxis=dict(
            title="%",
            showgrid=False,
            zeroline=False,
            dtick=1,
            tick0=0,
            tickfont=dict(color="white"),
        )
    )

    return fig
