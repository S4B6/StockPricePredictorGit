# history/charts/rates/policy_rates/line_regime.py

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def render(df, title):
    """
    Line chart with regime shading (Hiking / Easing).
    FULL VERSION:
    - processes raw SQL (multiple MM rates)
    - filters days with >=5 series
    - computes daily average
    - applies 5-day MA
    - tags regimes
    - renders shaded line chart
    """

    # ------------------------------------------------------
    # STEP 1 — RAW → CLEAN
    # ------------------------------------------------------
    df = df.dropna(subset=["value"]).copy()
    df["date"] = pd.to_datetime(df["date"])

    # ------------------------------------------------------
    # STEP 2 — Pivot to wide format
    # ------------------------------------------------------
    pivot = (
        df.pivot(index="date", columns="indicator_code", values="value")
          .sort_index()
    )

    # ------------------------------------------------------
    # STEP 3 — Keep only dates with ≥5 available MM rates
    # ------------------------------------------------------
    good_days = pivot.count(axis=1) >= 5
    pivot = pivot[good_days]

    # ------------------------------------------------------
    # STEP 4 — Daily average
    # ------------------------------------------------------
    daily_avg = pivot.mean(axis=1)

    df_avg = daily_avg.to_frame(name="value")
    df_avg["series"] = "Average 5d MA Eligible MM Rates"

    # ------------------------------------------------------
    # STEP 5 — 5-day moving average
    # ------------------------------------------------------
    df_avg["value"] = df_avg["value"].rolling(window=5, min_periods=1).mean()

    # ------------------------------------------------------
    # STEP 6 — Regime tagging (Python only)
    # ------------------------------------------------------
    def detect_regime(d):

        # 0) ???: ???
        if pd.Timestamp("1999-01-01") <= d < pd.Timestamp("1999-06-17"):
            return "Easing"
        
        # 1) 1999–2000: hiking into the dot-com peak
        if pd.Timestamp("1999-08-23") <= d < pd.Timestamp("2000-10-06"):
            return "Hiking"

        # 2) 2000–2003: easing
        if pd.Timestamp("2001-01-08") <= d < pd.Timestamp("2002-01-29"):
            return "Easing"

        # 2 bis) 2000–2003: easing
        if pd.Timestamp("2003-01-06") <= d < pd.Timestamp("2003-08-08"):
            return "Easing"

        # 3) 2003–2007: hiking pre-GFC
        if pd.Timestamp("2004-04-21") <= d < pd.Timestamp("2007-09-26"):
            return "Hiking"

        # 4) 2007–2009: crisis easing
        if pd.Timestamp("2007-10-30") <= d < pd.Timestamp("2009-10-07"):
            return "Easing"

        # 5) 2010–2011: small hiking hump
        if pd.Timestamp("2010-02-19") <= d < pd.Timestamp("2011-06-24"):
            return "Hiking"

        # 6) 2011–2013: easing again
        if pd.Timestamp("2011-06-24") <= d < pd.Timestamp("2015-05-21"):
            return "Easing"

        # 8) 2018–early 2020: hiking
        if pd.Timestamp("2017-02-02") <= d < pd.Timestamp("2019-01-01"):
            return "Hiking"

        # 9) 2020–early: Covid easing
        if pd.Timestamp("2019-09-23") <= d < pd.Timestamp("2020-04-09"):
            return "Easing"

        # 10) 2022–late 2023: aggressive hiking
        if pd.Timestamp("2022-02-04") <= d < pd.Timestamp("2024-01-08"):
            return "Hiking"

        # 11) late 2023 onward: easing / rollover
        if pd.Timestamp("2024-05-03") <= d:
            return "Easing"

        return None

    df_avg["regime"] = df_avg.index.to_series().apply(detect_regime)

    # ------------------------------------------------------
    # STEP 7 — Now continue with your existing chart logic
    # ------------------------------------------------------
    df = df_avg.reset_index()
    df = df.sort_values("date")

    # ----- COLOR LABELS -----
    def color_regime(r):
        if r == "Hiking":
            return "<span style='color:#ff0000;'><b>Hiking</b></span>"
        if r == "Easing":
            return "<span style='color:#00CC00;'><b>Easing</b></span>"
        return ""

    df["regime_color"] = df["regime"].apply(color_regime)

    # ------------------------------------------------------
    # FIGURE INIT
    # ------------------------------------------------------
    fig = go.Figure()

    # MAIN LINE
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["value"],
        mode="lines",
        customdata=df["regime_color"],
        line=dict(width=1.8, color="white"),
        hovertemplate="%{y:.2f}%<br><b>%{customdata}</b><extra></extra>",
        showlegend=False
    ))

    # ------------------------------------------------------
    # BUILD SHADING (REGIME BLOCKS)
    # ------------------------------------------------------
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

    # ------------------------------------------------------
    # CUSTOM GRIDLINES
    # ------------------------------------------------------
    y_min = df["value"].min()
    y_max = df["value"].max()

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

    # Vertical every 4 years
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

    # ------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(family="Courier Prime", color="white"),

        margin=dict(l=40, r=40, t=40, b=40),
        height=250,
        hovermode="x",

        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font=dict(family="Courier Prime", color="black", size=13)
        ),

        xaxis=dict(
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
            tickfont=dict(color="white"),
        )
    )

    return fig
