import pandas as pd
import plotly.express as px
from django.shortcuts import render, get_object_or_404
from sqlalchemy import create_engine
from django.http import HttpResponse
import io
from django.utils.html import escape
from urllib.parse import quote
from django.urls import reverse
from .models import HistoryPage, HistoryChart

def history_category(request, category):
    return render(request, "history/category.html", {"category": category.capitalize()})

def history_home(request):
    return render(request, "history/history.html")

def history_detail(request, slug):
    page = get_object_or_404(HistoryPage, slug=slug)

    engine = create_engine(
        "postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db"
    )

    # 1) Always start with the raw HTML content
    content_html = page.content or ""
    charts_data = []

    # 2) Build chart html blocks
    for chart in page.charts.all().order_by("order"):
        df = pd.read_sql(chart.sql_query, engine)
        fig = make_clean_plot(df, chart.chart_type, chart.title)

        html = fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            config=dict(
                displayModeBar=False,
                scrollZoom=False,
                staticPlot=False,
            ),
        )

        charts_data.append({
            "title": chart.title,
            "html": html,
            "show_download": chart.show_download,
        })

    # 3) Replace [CHART1], [CHART2], ... placeholders (if any)
    leftover_blocks = []

    for idx, c in enumerate(charts_data, start=1):
        placeholder = f"[CHART{idx}]"

        download_url = (
            reverse("history_download")
            + f"?slug={quote(page.slug, safe='')}&chart={quote(c['title'], safe='')}"
            if c["show_download"] else ""
        )

        chart_block = f"""
        <div class="history-chart-block">
            <div class="chart-header-center">
                <span class="chart-title">{escape(c['title'])}</span>
                {(
                    f'<a class="chart-download-btn" data-download '
                    f'href="{download_url}" title="Download CSV">⬇</a>'
                ) if download_url else ""}
            </div>
            <div class="history-chart">
                {c['html']}
            </div>
        </div>
        """

        if placeholder in content_html:
            content_html = content_html.replace(placeholder, chart_block)
        else:
            leftover_blocks.append(chart_block)

    if leftover_blocks:
        content_html += "\n".join(leftover_blocks)

    return render(request, "history/detail.html", {
        "page": page,
        "content_html": content_html,
        "theme": page.asset_class.lower(),
    })


def make_clean_plot(df, chart_type, title):

    """
    Generic chart builder using your ECB-style formatting
    for ALL charts (line, area, bar).
    Assumes at least columns: date, value.
    Optionally:
      - a 'series' column like 'indicator_code' for colors
      - a 'line_style' column to control dash/solid per series
    """

    # Detect series column
    color_col = None
    for candidate in ["indicator_code", "series", "name", "label"]:
        if candidate in df.columns:
            color_col = candidate
            break

    # Detect optional style column
    style_col = None
    for candidate in ["line_style", "style", "dash", "linetype"]:
        if candidate in df.columns:
            style_col = candidate
            break

    # ---- 1) Base figure by type ----
    
    # -----------------------------------------
    # SPECIAL CASE: MAD HYBRID DISPERSION CHART
    # -----------------------------------------
    if chart_type == "mad_hybrid":
        import numpy as np
        import plotly.graph_objects as go

        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        # ---- Pivot + ffill(limit=4)
        pivot = df.pivot(index="date", columns="indicator_code", values="value")
        pivot = pivot.sort_index()
        pivot = pivot.asfreq("D")
        pivot = pivot.ffill(limit=4)

        # ---- Hybrid MAD
        def mad_hybrid(row):
            vals = row.dropna()
            if len(vals) < 2:
                return np.nan
            med = vals.median()
            return np.mean(np.abs(vals - med))

        mad_series = pivot.apply(mad_hybrid, axis=1).dropna()

        # ------------------------------------------
        # FIGURE
        # ------------------------------------------
        fig = go.Figure()

        # ------------------------------------------
        # SHADING ZONES (clean colors + hovertext)
        # ------------------------------------------

        # Convergence zone (<0.3)
        fig.add_hrect(
            y0=0, y1=0.3,
            fillcolor="rgba(0,102,204,0.13)",
            line_width=0,
            layer="below",
        )

        # Divergence zone (>1.0)
        fig.add_hrect(
            y0=1.0, y1=max(mad_series)*1.05,
            fillcolor="rgba(255,80,80,0.15)",
            line_width=0,
            layer="below",
        )
        # ------------------------------------------
        # MAIN LINE
        # ------------------------------------------
        fig.add_trace(go.Scatter(
            x=mad_series.index,
            y=mad_series.values,
            mode="lines",
            line=dict(color="white", width=1.8),
            hovertemplate="%{y:.2f} pp<extra></extra>",
            showlegend=False
        ))

        # ------------------------------------------
        # REMOVE DEFAULT GRIDLINES
        # (we draw dashed ones manually below)
        # ------------------------------------------
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)

        # ------------------------------------------
        # MANUALLY DRAW DASHED GRIDLINES
        # ------------------------------------------

        # Horizontal: every 0.2
        y_ticks = np.arange(0, mad_series.max()+0.01, 0.2)
        for y in y_ticks:
            fig.add_shape(
                type="line",
                x0=mad_series.index.min(),
                x1=mad_series.index.max(),
                y0=y, y1=y,
                line=dict(
                    color="rgba(255,255,255,0.3)",  # softer fade
                    width=1,
                    dash="dot"                  # VERY subtle dash pattern
                ),
                layer="below"
            )

        # Vertical: every 4 years (2000, 2004, 2008…)
        years = mad_series.index.year.unique()
        for year in years:
            if year % 4 == 0:
                fig.add_shape(
                    type="line",
                    x0=f"{year}-01-01",
                    x1=f"{year}-01-01",
                    y0=0,
                    y1=mad_series.max()*1.05,
                    line=dict(
                        color="rgba(255,255,255,0.30)",
                        width=1,
                        dash="dot"
                    ),
                    layer="below"
                )

        # ------------------------------------------
        # LAYOUT
        # ------------------------------------------
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="black",
            plot_bgcolor="black",
            font=dict(family="Courier Prime", color="white", size=12),

            margin=dict(l=40, r=40, t=10, b=10),
            height=250,

            xaxis=dict(
                tickformat="%Y",
                dtick="M48",
                hoverformat="%d %b %Y",
            ),

            yaxis=dict(
                title="pp",   # Smaller label, clean
                dtick=0.2,
                titlefont=dict(size=10),

            ),

            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Courier Prime",
                font_color="black",
                bordercolor="white",
                align="left",
            ),


            hovermode="x",
        )

        return fig



    # -------------------------------
    # LINE - REGIME
    # -------------------------------
    if chart_type == "line_regime":
        import plotly.graph_objects as go

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        fig = go.Figure()

        # Make colored regime label for hover
        def color_regime(r):
            if r == "Hiking":
                return "<span style='color:#ff0000;'><b>Hiking</b></span>"
            if r == "Easing":
                return "<span style='color:#00CC00;'><b>Easing</b></span>"
            return ""

        df["regime_color"] = df["regime"].apply(color_regime)

        # ------------------------
        # MAIN LINE
        # ------------------------
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["value"],
            mode="lines",
            customdata=df["regime_color"],
            line=dict(
                width=1.8,
                color="white",
            ),
            hovertemplate=(
            "%{y:.2f}%<br>"                      # value
            "<b>%{customdata}</b>"       # regime
            "<extra></extra>"            
            ),
        ))

        # ------------------------
        # SHADING (EASING / HIKING)
        # ------------------------
        if "regime" in df.columns:
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

            # Correct colors
            COLORS = {
                "Hiking": "rgba(255, 155, 155, 0.8)",   # bright red
                "Easing": "rgba(150, 255, 150, 0.8)", # bright green
            }

            for (x0, x1, reg) in blocks:
                fig.add_vrect(
                    x0=x0,
                    x1=x1,
                    fillcolor=COLORS.get(reg, "rgba(255,255,255,0.8)"),
                    line_width=0,
                    opacity=0.8,
                    layer="below",
                )

        # ------------------------
        # LAYOUT (MATCHES YOUR WEBSITE)
        # ------------------------
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font_family="Courier Prime",
            font_color="white",

            title=dict(
                text="",  # chart title
                x=0.5,
                font=dict(color="white", size=18)
            ),

            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Courier Prime",
                font_color="black",
                bordercolor="white",
                align="left",
            ),

            xaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                dtick="M48",
                tickfont=dict(color="white"),
                hoverformat="%d %b %Y"
            ),
            yaxis=dict(
                title="%",
                showgrid=False,
                zeroline=False,
                tickfont=dict(color="white"),
            ),

            margin=dict(l=40, r=40, t=10, b=10),
            height=250,
            hovermode="x",

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)"
            )

           
        )

        fig.update_xaxes(
            tickfont=dict(family="Courier Prime", color="white"),
            titlefont=dict(family="Courier Prime", color="white"),
        )

        fig.update_yaxes(
            dtick=1,  # force 1,2,3,4 instead of 0,2,4
            tick0=0,
            tickfont=dict(family="Courier Prime", color="white"),
            titlefont=dict(family="Courier Prime", color="white"),
            showgrid=False,
        )


        # ----------- Custom dashed gridlines (horizontal) -----------
        import numpy as np

        y_min = df["value"].min()
        y_max = df["value"].max()
        y_ticks = np.arange(np.floor(y_min), np.ceil(y_max)+0.1, 1)

        for y in y_ticks:
            fig.add_shape(
                type="line",
                x0=df["date"].min(),
                x1=df["date"].max(),
                y0=y, y1=y,
                line=dict(
                    color="rgba(255,255,255,0.25)",
                    width=1,
                    dash="dot",
                ),
                layer="below"
            )

        # ----------- Custom dashed gridlines (vertical every 4 years) -----------
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
                    line=dict(
                        color="rgba(255,255,255,0.25)",
                        width=1,
                        dash="dot",
                    ),
                    layer="below"
                )


        return fig



    
    # -------------------------------
    # SPECIAL CASE: MONEY-MARKET HEATMAP
    # -------------------------------
    if chart_type == "heatmap_mm":
        # df must contain: date, value, indicator_code
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        pivot = df.pivot(index="date", columns="indicator_code", values="value")
        pivot = pivot.sort_index()

        years = pivot.index.year.unique()
        last_full_year = years[-2]
        current_year = years[-1]

        # ---- Yearly ----
        yearly = pivot[pivot.index.year < last_full_year].resample("YE").mean()
        yearly.index = yearly.index.year.astype(str)

        # ---- Quarterly ----
        quarterly = pivot[pivot.index.year == last_full_year].resample("QE").mean()
        quarterly.index = quarterly.index.to_period("Q").strftime("%Y-Q%q")

        # ---- Monthly ----
        monthly = pivot[pivot.index.year == current_year].resample("ME").mean()
        monthly.index = monthly.index.to_period("M").astype(str)

        # ---- Combined ----
        combined = pd.concat([yearly, quarterly, monthly], axis=0).T

        # ---- Plotly Heatmap ----
        import plotly.graph_objects as go

        # Custom colorscale (high rates = warm, low rates = cool)
        custom_scale = [
            [0.00, "#0a0535"],   # deep navy (very low)
            [0.25, "#264976"],   # cool blue
            [0.50, "#3fa6a6"],   # teal
            [0.75, "#f4d35e"],   # sand yellow
            [1.00, "#ee3b3b"],   # red (very high rates)
        ]

        fig = go.Figure(
            data=go.Heatmap(
                z=combined.values,
                x=list(combined.columns),
                y=list(combined.index),
                colorscale=custom_scale,
                colorbar=dict(
                    title="%",
                    tickfont=dict(family="Courier Prime"),
                    titlefont=dict(family="Courier Prime"),
                ),
                hoverongaps=False,
                hovertemplate="<b>%{y}</b><br>Period: %{x}<br>Average rate: %{z:.2f}%<extra></extra>",
            )
        )

        # ---- X-Axis label cleanup: show only last 2 digits for years
        pretty_x = []
        for col in combined.columns:
            if "-" not in col:   # yearly (e.g. 1999)
                pretty_x.append(col[-2:])  # "99"
            elif "-Q" in col:    # quarter (e.g. 2024-Q1)
                yr = col[:4]
                q  = col[-2:]
                pretty_x.append(yr[-2:] + "-" + q)  # "24-Q1"
            else:                # monthly (e.g. 2025-11)
                yr = col[:4]
                m  = col[-2:]
                # convert month → name
                import calendar
                pretty_x.append(yr[-2:] + "-" + calendar.month_abbr[int(m)])
                # -> "25-Nov"

        fig.update_xaxes(
            ticktext=pretty_x,
            tickvals=list(range(len(pretty_x))),
            tickangle=45,
            tickfont=dict(family="Courier Prime", size=11),
        )

        # ---- Y Axis font
        fig.update_yaxes(
            tickfont=dict(family="Courier Prime", size=12),
            autorange="reversed",
        )

        # ---- Layout cleanup: remove top extra space
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d0017",
            plot_bgcolor="#0d0017",
            margin=dict(l=50, r=50, t=30, b=80),   # 🔥 tighter top margin
            height=550,
            font=dict(family="Courier Prime", color="#FFFFFF"),
            title=dict(
                text="",
                x=0.5,
                y=0.95,
                font=dict(family="Courier Prime", size=20, color="#FFFFFF"),
            ),
        )

        # ---- ensure unified hover box like your line charts ----
        fig.update_layout(
            hovermode="x",
            hoverlabel=dict(
                bgcolor="#0d0017",
                font_size=13,
                font_family="Courier Prime",
                font_color="#FFFFFF",
                bordercolor="#0d0017",
                align="left",
            ),
        )


        fig.update_layout(spikedistance=-1)
        fig.update_xaxes(showspikes=False)
        fig.update_yaxes(showspikes=False)

        # ---- Remove gridlines (cleaner visual)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

        # ---- Softer separators (light grey instead of white)
        year_end  = len(yearly.index)
        quarter_end = len(yearly.index) + len(quarterly.index)

        fig.add_vline(x=year_end - 0.5,   line_width=1.5, line_color="white")
        fig.add_vline(x=quarter_end - 0.5, line_width=1.5, line_color="white")

        return fig



    if chart_type == "line":
        if color_col:
            fig = px.line(
                df,
                x="date",
                y="value",
                color=color_col,
                line_shape="hv",
            )
        else:
            fig = px.line(df, x="date", y="value", line_shape="hv")
    elif chart_type == "area":
        if color_col:
            fig = px.area(df, x="date", y="value", color=color_col)
        else:
            fig = px.area(df, x="date", y="value")
    else:  # "bar"
        if color_col:
            fig = px.bar(df, x="date", y="value", color=color_col)
        else:
            fig = px.bar(df, x="date", y="value")

    fig.update_layout(legend_title_text="")

    # ---- 2) Universal styling ----
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d0017",
        plot_bgcolor="#0d0017",
        font=dict(family="Courier Prime", color="#ffffff", size=13),
        title=None,
        xaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#ffffff"),
        ),
        yaxis=dict(
            title="%",
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#ffffff"),
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
        margin=dict(l=40, r=40, t=40, b=40),
        height=420,
        hovermode="x unified",
        xaxis_hoverformat="%d %b %Y",
    )

     # Generic trace style
    fig.update_traces(
        mode="lines",
        marker=dict(size=0),
        hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}%<extra></extra>",
    )

    # If SQL provided a line_width column, use it
    if "line_width" in df.columns:
        # Need a mapping series -> width
        color_col = None
        for candidate in ["indicator_code", "series", "name", "label"]:
            if candidate in df.columns:
                color_col = candidate
                break

        if color_col:
            width_map = {
                row[color_col]: float(row["line_width"])
                for _, row in df[[color_col, "line_width"]].drop_duplicates(subset=[color_col]).iterrows()
            }

            def _apply_width(trace):
                w = width_map.get(trace.name)
                if w is not None:
                    trace.update(line=dict(width=w))

            fig.for_each_trace(_apply_width)
        else:
            # no series column -> one line, just take first width
            w = float(df["line_width"].iloc[0])
            fig.update_traces(line=dict(width=w))
    else:
        # default width if nothing provided
        fig.update_traces(line=dict(width=2.2))


    return fig


def download_chart_csv(request):
    slug = request.GET.get("slug")
    chart_title = request.GET.get("chart")

    page = get_object_or_404(HistoryPage, slug=slug)
    chart = get_object_or_404(
        HistoryChart,
        page=page,
        title__iexact=chart_title.strip()
    )

    engine = create_engine("postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db")
    
    df = pd.read_sql(chart.sql_query, engine)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    filename = chart_title.lower().replace(" ", "_") + ".csv"

    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response