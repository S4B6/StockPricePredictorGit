# history/charts/generic/line.py

import plotly.express as px
import plotly.graph_objects as go


def render(df, title):
    """
    Generic line chart (ECB-style)
    - dark theme
    - unified hover
    - adaptive hover font size 
    - supports: indicator_code / name / series
    - supports: line_width column
    - supports: line_style column (dash)
    """

    # ---------------------------------------------------------
    # Detect color/series column
    # ---------------------------------------------------------
    color_col = None
    for c in ["indicator_code", "series", "name", "label"]:
        if c in df.columns:
            color_col = c
            break

    # ---------------------------------------------------------
    # Base figure
    # ---------------------------------------------------------
    if color_col:
        fig = px.line(
            df,
            x="date",
            y="value",
            color=color_col,
            line_shape="hv",
        )
    else:
        fig = px.line(
            df,
            x="date",
            y="value",
            line_shape="hv"
        )

    fig.update_layout(legend_title_text="")

    # Number of series → dynamic hover font
    if color_col:
        n_series = df[color_col].nunique()
    else:
        n_series = 1

    if n_series <= 6:
        hover_font = 13
    elif n_series <= 8:
        hover_font = 12
    else:
        hover_font = 10


    # ---------------------------------------------------------
    # Dynamic line width based on number of series
    # ---------------------------------------------------------
    if n_series <= 4:
        auto_width = 2.6
    elif n_series <= 7:
        auto_width = 2.2
    elif n_series <= 12:
        auto_width = 1.8
    else:
        auto_width = 1.4

    # ---------------------------------------------------------
    # UNIVERSAL STYLE (ECB-style)
    # ---------------------------------------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d0017",
        plot_bgcolor="#0d0017",

        font=dict(family="Courier Prime", color="#ffffff", size=13),

        xaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
        ),
        yaxis=dict(
            title="%",
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#ffffff"),
        ),

        margin=dict(l=40, r=40, t=10, b=40),

        height=420,
        hovermode="x unified",
        xaxis_hoverformat="%d %b %Y",

        hoverlabel=dict(
            font_size=hover_font,
            font_family="Courier Prime",
            align="left",
        ),
    )

    # ---------------------------------------------------------
    # APPLY TRACE-WIDE CUSTOM STYLE
    # ---------------------------------------------------------
    fig.update_traces(
        mode="lines",
        marker=dict(size=0),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{y:.2f}%<extra></extra>"
        ),
    )

    # ---------------------------------------------------------
    # Optional: line_width per series
    # ---------------------------------------------------------
    if "line_width" in df.columns:

        # Determine the series column again
        series = color_col

        if series:
            # Map each series → width
            width_map = {
                row[series]: float(row["line_width"])
                for _, row in df[[series, "line_width"]].drop_duplicates(subset=[series]).iterrows()
            }

            def apply_width(trace):
                w = width_map.get(trace.name)
                if w is not None:
                    trace.update(line=dict(width=w))

            fig.for_each_trace(apply_width)

        else:
            # No series → single-line chart
            fig.update_traces(line=dict(width=float(df["line_width"].iloc[0])))

    else:
        # Default width = auto depending on number of series
        fig.update_traces(line=dict(width=auto_width))

    # ---------------------------------------------------------
    # Optional: line_style (dash)
    # ---------------------------------------------------------
    if "line_style" in df.columns and color_col:
        style_map = {
            row[color_col]: row["line_style"]
            for _, row in df[[color_col, "line_style"]].drop_duplicates(subset=[color_col]).iterrows()
        }

        def apply_dash(trace):
            dash = style_map.get(trace.name)
            if dash:
                trace.update(line=dict(dash=dash))

        fig.for_each_trace(apply_dash)

    return fig
