import numpy as np
import pandas as pd
import plotly.graph_objects as go


def render(df, title):
    """
    Money-Market Hybrid MAD (median-based average deviation)
    - ffill(limit=4)
    - Convergence & divergence shading
    - Custom dashed gridlines
    - Unified hover style
    """

    # -------------------------
    # CLEAN DATA
    # -------------------------
    df = df.dropna(subset=["value"])

    pivot = df.pivot(index="date", columns="indicator_code", values="value")
    pivot = pivot.sort_index()
    pivot = pivot.asfreq("D").ffill(limit=4)

    # -------------------------
    # HYBRID MAD FUNCTION
    # -------------------------
    def mad_hybrid(row):
        vals = row.dropna()
        if len(vals) < 2:
            return np.nan
        med = vals.median()
        return np.mean(np.abs(vals - med))

    mad = pivot.apply(mad_hybrid, axis=1).dropna()

    # -------------------------
    # BASE FIGURE
    # -------------------------
    fig = go.Figure()

    # -------------------------
    # SHADING ZONES
    # -------------------------
    fig.add_hrect(
        y0=0,
        y1=0.4,
        fillcolor="#0184FF",
        opacity=0.30,
        line_width=0,
        layer="below",
    )

    fig.add_hrect(
        y0=1.0,
        y1=float(mad.max()) * 1.05,
        fillcolor="#861313",
        opacity=0.30,
        line_width=0,
        layer="below",
    )

    # -------------------------
    # MAIN LINE
    # -------------------------
    fig.add_trace(go.Scatter(
        x=mad.index,
        y=mad.values,
        mode="lines",
        line=dict(color="white", width=1.8),
        hovertemplate="%{y:.2f} pp<extra></extra>",
        showlegend=False
    ))

    # remove default grid, re-add custom
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    # -------------------------
    # CUSTOM GRIDLINES
    # -------------------------

    # Horizontal every 0.2
    y_ticks = np.arange(0, mad.max() + 0.001, 0.2)
    for y in y_ticks:
        fig.add_shape(
            type="line",
            x0=mad.index.min(),
            x1=mad.index.max(),
            y0=y, y1=y,
            line=dict(
                color="rgba(255,255,255,0.30)",
                width=1,
                dash="dot"
            ),
            layer="below"
        )

    # Vertical every 4 years
    for year in mad.index.year.unique():
        if year % 4 == 0:
            fig.add_shape(
                type="line",
                x0=f"{year}-01-01",
                x1=f"{year}-01-01",
                y0=0,
                y1=mad.max() * 1.05,
                line=dict(
                    color="rgba(255,255,255,0.3)",
                    width=1,
                    dash="dot",
                ),
                layer="below"
            )

    # -------------------------
    # LAYOUT
    # -------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=250,
        margin=dict(l=40, r=40, t=40, b=40),

        font=dict(
            family="Courier Prime",
            color="white",
            size=12
        ),

        xaxis=dict(
            tickformat="%Y",
            dtick="M48",
            hoverformat="%d %b %Y",
        ),

        yaxis=dict(
            title="pp",
            dtick=0.2,
            titlefont=dict(size=10),
        ),

        hovermode="x",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font_size=13,
            font_family="Courier Prime",
            font_color="black",
            align="left",
        ),
    )

    return fig
