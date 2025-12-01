import pandas as pd
import numpy as np
import plotly.express as px
from django.shortcuts import render, get_object_or_404
from sqlalchemy import create_engine
from django.http import HttpResponse
import io
from django.utils.html import escape
from urllib.parse import quote
from django.urls import reverse
from .models import HistoryPage, HistoryChart
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import calendar
from functools import lru_cache
import re
from history.charts.registry import get_chart_renderer
from history.chart_loader import load_chart_renderer


engine = create_engine(
    "postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db"
)

# ======================================================================
# CATEGORY + HOME
# ======================================================================

def history_category(request, category):
    return render(request, "history/category.html", {"category": category.capitalize()})

def history_home(request):
    return render(request, "history/history.html")

# ======================================================================
# DETAIL PAGE — FIXED (no duplicates, bubble maps hidden, fast)
# ======================================================================

def history_detail(request, slug):
    page = get_object_or_404(HistoryPage, slug=slug)

    # 1) Start with page content
    content_html = page.content or ""
    charts_data = []

    # 2) Build placeholders
    for chart in page.charts.all().order_by("order"):

        chart_type = (chart.chart_type or "").lower()

        # Hide download button for bubble maps
        if "bubble" in chart_type:
            final_show_download = False
        else:
            final_show_download = chart.show_download

        download_url = (
            reverse("history_download")
            + f"?slug={quote(page.slug, safe='')}&chart={quote(chart.title, safe='')}"
            if final_show_download else ""
        )

        placeholder_html = f"""
            <div class="history-chart-block">
                <div class="chart-header-center">
                    <span class="chart-title">{escape(chart.title)}</span>
                    {(
                        f'<a class="chart-download-btn" data-download '
                        f'href="{download_url}" title="Download CSV">⭳</a>'
                    ) if final_show_download else ""}
                </div>

                <div class="history-chart"
                    id="chart-{chart.id}"
                    data-chart-id="{chart.id}">
                    <div class="chart-loading">Loading chart...</div>
                </div>
            </div>
        """

        charts_data.append({
            "title": chart.title,
            "html": placeholder_html,
            "show_download": final_show_download,
        })

    # 3) Replace placeholders — FIXED (no duplicates, case-insensitive)
    for idx, c in enumerate(charts_data, start=1):
        placeholder = f"[CHART{idx}]"

        # case-insensitive replacement
        pattern = re.compile(re.escape(placeholder), flags=re.IGNORECASE)

        if re.search(pattern, content_html):
            content_html = re.sub(pattern, c["html"], content_html)

    # 4) NO leftover_blocks — removed because it caused duplicates
    # (Do NOT append charts automatically at bottom)

    return render(request, "history/detail.html", {
        "page": page,
        "content_html": content_html,
        "theme": page.asset_class.lower(),
    })


# ======================================================================
# CLEAN PLOT
# ======================================================================

def make_clean_plot(df, chart_type, title):

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    renderer = load_chart_renderer(chart_type)
    return renderer(df, title)

# ======================================================================
# CSV EXTRACTION — FIXED & SAFE
# ======================================================================

def extract_chart_data_for_csv(fig, chart_type, chart_title):
    rows = []

    for trace in fig.data:

        # ---------------------------------------------------------
        # 1) LINE / SCATTER (including multi-series)
        # ---------------------------------------------------------
        if isinstance(trace, (go.Scatter, go.Scattergl)):
            x_vals = trace["x"]
            y_vals = trace["y"]
            name = trace.name or chart_title

            for x, y in zip(x_vals, y_vals):
                rows.append({
                    "date": x,
                    "value": y,
                    "series": name,
                })

        # ---------------------------------------------------------
        # 2) HEATMAP — return full matrix (best behaviour)
        # ---------------------------------------------------------
        elif isinstance(trace, go.Heatmap):
            x_labels = list(trace["x"])     # columns
            y_labels = list(trace["y"])     # rows
            z_matrix = trace["z"]           # 2D matrix

            df = pd.DataFrame(z_matrix, index=y_labels, columns=x_labels)
            df = df.reset_index()
            df.rename(columns={"index": "indicator_code"}, inplace=True)
            return df    # RETURN IMMEDIATELY (simple, clean, correct)

        # ---------------------------------------------------------
        # 3) Other trace types: ignored here (bubble maps handled in view)
        # ---------------------------------------------------------

    # If no rows collected → empty df
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # For line / regime charts → pivot to wide format:
    ct = (chart_type or "").lower()
    if "line" in ct or "regime" in ct:
        try:
            wide = df.pivot(index="date", columns="series", values="value").reset_index()
            wide.columns.name = None  # remove "series" name from columns
            return wide
        except Exception:
            # in case anything weird happens, just fall back to long format
            return df

    # For non-line charts that still use Scatter, keep long format
    return df

# ======================================================================
# DOWNLOAD CSV — FAST VERSION
# ======================================================================

def download_chart_csv(request):
    slug = request.GET.get("slug")
    chart_title = request.GET.get("chart")

    page = get_object_or_404(HistoryPage, slug=slug)
    chart = get_object_or_404(
        HistoryChart,
        page=page,
        title__iexact=chart_title.strip()
    )

    chart_type = (chart.chart_type or "").lower()

    # Load raw SQL
    df_raw = pd.read_sql(chart.sql_query, engine)

    # ---------------------------------------------------------
    # BUBBLE MAPS → NO DOWNLOAD
    # ---------------------------------------------------------
    if "bubble" in chart_type:
        return HttpResponse(
            "No downloadable dataset for bubble maps.",
            content_type="text/plain",
            status=204
        )

    # ---------------------------------------------------------
    # HEATMAP → export EXACT Plotly matrix
    # ---------------------------------------------------------
    if "heat" in chart_type:
        fig = make_clean_plot(df_raw, chart.chart_type, chart.title)
        df_export = extract_chart_data_for_csv(fig, chart.chart_type, chart_title)

    # ---------------------------------------------------------
    # LINE / REGIME → processed result
    # ---------------------------------------------------------
    elif "line" in chart_type or "regime" in chart_type:
        fig = make_clean_plot(df_raw, chart.chart_type, chart.title)
        df_export = extract_chart_data_for_csv(fig, chart.chart_type, chart_title)

    # ---------------------------------------------------------
    # EVERYTHING ELSE → raw SQL
    # ---------------------------------------------------------
    else:
        df_export = df_raw

    # Export CSV
    buffer = io.StringIO()
    df_export.to_csv(buffer, index=False)
    buffer.seek(0)

    filename = chart_title.lower().replace(" ", "_") + ".csv"

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# ======================================================================
# FETCH CHART
# ======================================================================

from django.http import HttpResponse, JsonResponse

def fetch_chart(request, chart_id):
    chart = get_object_or_404(HistoryChart, id=chart_id)

    df = pd.read_sql(chart.sql_query, engine)
    fig = make_clean_plot(df, chart.chart_type, chart.title)

    return HttpResponse(
        fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            config=dict(
                displayModeBar=False,
                scrollZoom=False,
                staticPlot=False,
            ),
        )
    )
