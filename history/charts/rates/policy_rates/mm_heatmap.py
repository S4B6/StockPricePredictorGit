# history/charts/rates/money_markets/heatmap_mm.py

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import calendar


def render(df, title):
    """
    Money-Market Heatmap (Yearly + Quarterly + Monthly)
    - Resamples long series into Y/Q/M blocks
    - Custom financial colorscale
    - Clean compressed axis labeling ("24-Q1", "25-Nov", etc.)
    - White separators between Y/Q/M blocks
    - Unified hover style
    """

    # -------------------------
    # CLEAN DATA
    # -------------------------
    df = df.dropna(subset=["value"])

    pivot = df.pivot(index="date", columns="indicator_code", values="value")
    pivot = pivot.sort_index()

    # -------------------------
    # YEAR / QUARTER / MONTH SPLITTING
    # -------------------------
    years = pivot.index.year.unique()
    last_full_year = years[-2]     # example: 2024
    current_year   = years[-1]     # example: 2025

    # ---- Yearly (< last full year)
    yearly = pivot[pivot.index.year < last_full_year].resample("YE").mean()
    yearly.index = yearly.index.year.astype(str)

    # ---- Quarterly (last full year)
    quarterly = pivot[pivot.index.year == last_full_year].resample("QE").mean()
    quarterly.index = quarterly.index.to_period("Q").strftime("%Y-Q%q")

    # ---- Monthly (current year)
    monthly = pivot[pivot.index.year == current_year].resample("ME").mean()
    monthly.index = monthly.index.to_period("M").astype(str)

    # ---- COMBINED
    combined = pd.concat([yearly, quarterly, monthly], axis=0).T

    # -------------------------
    # CUSTOM COLORSCALE
    # -------------------------
    custom_scale = [
        [0.00, "#0a0535"],   # deep navy
        [0.25, "#264976"],   # cool blue
        [0.50, "#3fa6a6"],   # teal
        [0.75, "#f4d35e"],   # warm yellow
        [1.00, "#ee3b3b"],   # red (high rates)
    ]

    # -------------------------
    # BUILD FIGURE
    # -------------------------
    fig = go.Figure(
        data=go.Heatmap(
            z=combined.values,
            x=list(combined.columns),
            y=list(combined.index),
            colorscale=custom_scale,
            hoverongaps=False,
            colorbar=dict(
                title="%",
                tickfont=dict(family="Courier Prime"),
                titlefont=dict(family="Courier Prime"),
            ),
            hovertemplate="<b>%{y}</b><br>Period: %{x}<br>Avg rate: %{z:.2f}%<extra></extra>",
        )
    )

    # -------------------------
    # CLEAN X LABELS (YY-QX / YY-MMM)
    # -------------------------
    pretty_x = []

    for col in combined.columns:

        # yearly like "1999"
        if "-" not in col:
            pretty_x.append(col[-2:])  # "99"
            continue

        # quarterly like "2024-Q2"
        if "-Q" in col:
            yr = col[:4]
            q  = col[-2:]
            pretty_x.append(yr[-2:] + "-" + q)
            continue

        # monthly like "2025-11"
        yr = col[:4]
        m  = col[-2:]
        pretty_x.append(yr[-2:] + "-" + calendar.month_abbr[int(m)])

    fig.update_xaxes(
        ticktext=pretty_x,
        tickvals=list(range(len(pretty_x))),
        tickangle=45,
        tickfont=dict(family="Courier Prime", size=11),
    )

    # -------------------------
    # Y AXIS CLEANUP
    # -------------------------
    fig.update_yaxes(
        autorange="reversed",
        tickfont=dict(family="Courier Prime", size=12),
    )

    # -------------------------
    # SEPARATORS BETWEEN Y / Q / M BLOCKS
    # -------------------------
    year_end      = len(yearly.index)
    quarter_end   = len(yearly.index) + len(quarterly.index)

    fig.add_vline(
        x=year_end - 0.5,
        line_width=1.5,
        line_color="white"
    )

    fig.add_vline(
        x=quarter_end - 0.5,
        line_width=1.5,
        line_color="white"
    )

    # -------------------------
    # UNIVERSAL CLEAN DARK LAYOUT
    # -------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d0017",
        plot_bgcolor="#0d0017",
        height=450,
        margin=dict(l=50, r=50, t=10, b=10),
        font=dict(family="Courier Prime", color="white"),

        hovermode="x",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font=dict(
                family="Courier Prime",
                size=13,
                color="black",
            )
        )
    )

    # clean up gridlines
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig
