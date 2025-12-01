# history/charts/rates/policy_rates/mm_bubble_map.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go


def render(df, title):
    """
    Money-Market Bubble Map:
    - x = mean level
    - y = volatility (std dev)
    - bubble size = |average correlation|
    - bubble color = signed average correlation
    - hover = full stats (min, max, first date, last date)
    - regression line (mean → volatility)
    """

    # -------------------------
    # CLEAN DATA
    # -------------------------
    df = df.dropna(subset=["value"])
    pivot = df.pivot(index="date", columns="indicator_code", values="value")
    pivot = pivot.sort_index()

    # -------------------------
    # BASIC STATS
    # -------------------------
    means = pivot.mean()
    stds = pivot.std()
    mins = pivot.min()
    maxs = pivot.max()
    first_dates = pivot.apply(lambda s: s.first_valid_index().strftime("%d %b %Y"))
    last_dates  = pivot.apply(lambda s: s.last_valid_index().strftime("%d %b %Y"))

    customdata = np.stack([
        mins.values,
        maxs.values,
        first_dates.values.astype(str),
        last_dates.values.astype(str),
    ], axis=-1)

    # -------------------------
    # CORRELATION STRUCTURE
    # -------------------------
    corr = pivot.corr()

    avg_corr = corr.apply(lambda row: row.drop(row.name).mean(), axis=1)
    avg_abs_corr = corr.apply(lambda row: row.drop(row.name).abs().mean(), axis=1)

    # -------------------------
    # FIGURE
    # -------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=means,
        y=stds,
        mode="markers+text",
        text=means.index,
        textposition="middle center",
        
        name="",              # 🔥 remove label
        showlegend=False,     # 🔥 no clickable legend

        customdata=customdata,

        marker=dict(
            size=avg_abs_corr * 120,
            color=avg_corr,
            colorscale="RdBu",
            showscale=True,
            colorbar=dict(
                title="Avg Corr",
                thickness=12,
                tickfont=dict(color="white"),
                titlefont=dict(color="white"),
            ),
            line=dict(color="black", width=0.5)
        ),

        hovertemplate=(
            "<b>%{text}</b><br>"
            "Mean: %{x:.3f}<br>"
            "Std: %{y:.3f}<br>"
            "Avg Corr: %{marker.color:.2f}<br>"
            "Min: %{customdata[0]:.3f}<br>"
            "Max: %{customdata[1]:.3f}<br>"
            "First: %{customdata[2]}<br>"
            "Last: %{customdata[3]}<extra></extra>"
        )
    ))

    # -------------------------
    # REGRESSION LINE
    # -------------------------
    X = means.values.reshape(-1, 1)
    Y = stds.values

    model = LinearRegression().fit(X, Y)

    x_min = X.min() - (X.max() - X.min()) * 0.2
    x_max = X.max() + (X.max() - X.min()) * 0.2

    x_line = np.linspace(x_min, x_max, 200)
    y_line = model.predict(x_line.reshape(-1, 1))

    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode="lines",
        line=dict(color="white", width=1, dash="dash"),
        hoverinfo="skip",
        showlegend=False,
        opacity=0.8
    ))

    # -------------------------
    # LAYOUT
    # -------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d0017",
        plot_bgcolor="#0d0017",
        height=450,
        margin=dict(l=40, r=40, t=10, b=40),
        font=dict(family="Courier Prime", color="white", size=12),

        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font=dict(
                family="Courier Prime",
                size=12,
                color="black"
            ),
        ),
    )

    fig.update_xaxes(
        title="Mean Level (%)",
        titlefont=dict(size=11),
        tickfont=dict(size=11),
        zeroline=False,
        showgrid=True,
        gridcolor="rgba(255,255,255,0.15)",
    )

    fig.update_yaxes(
        title="Volatility (Std Dev)",
        titlefont=dict(size=11),
        tickfont=dict(size=11),
        zeroline=False,
        showgrid=True,
        gridcolor="rgba(255,255,255,0.15)",
    )

    return fig
