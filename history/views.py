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

engine = create_engine(
    "postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db"
)

def history_category(request, category):
    return render(request, "history/category.html", {"category": category.capitalize()})

def history_home(request):
    return render(request, "history/history.html")

def history_detail(request, slug):
    page = get_object_or_404(HistoryPage, slug=slug)

    # 1) Always start with the raw HTML content
    content_html = page.content or ""
    charts_data = []

    # 2) Build chart placeholders (async loading)
    for chart in page.charts.all().order_by("order"):

        download_url = (
            reverse("history_download")
            + f"?slug={quote(page.slug, safe='')}&chart={quote(chart.title, safe='')}"
            if chart.show_download else ""
        )

        placeholder_html = f"""
            <div class="history-chart-block">
                <div class="chart-header-center">
                    <span class="chart-title">{escape(chart.title)}</span>
                    {(
                        f'<a class="chart-download-btn" data-download '
                        f'href="{download_url}" title="Download CSV">⭳</a>'
                    ) if chart.show_download else ""}
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

        chart_block = c["html"]

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


from history.charts.registry import get_chart_renderer

from history.chart_loader import load_chart_renderer

def make_clean_plot(df, chart_type, title):

    # safe normalization
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Load correct renderer
    renderer = load_chart_renderer(chart_type)

    # Call the renderer
    return renderer(df, title)




def download_chart_csv(request):
    slug = request.GET.get("slug")
    chart_title = request.GET.get("chart")

    page = get_object_or_404(HistoryPage, slug=slug)
    chart = get_object_or_404(
        HistoryChart,
        page=page,
        title__iexact=chart_title.strip()
    )
    
    df = pd.read_sql(chart.sql_query, engine)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    filename = chart_title.lower().replace(" ", "_") + ".csv"

    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


from django.http import HttpResponse, JsonResponse

def fetch_chart(request, chart_id):
    """
    Returns the Plotly HTML for a given chart ID (async loading).
    """
    chart = get_object_or_404(HistoryChart, id=chart_id)

    # load data
    df = pd.read_sql(chart.sql_query, engine)

    # clean + render plot
    fig = make_clean_plot(df, chart.chart_type, chart.title)

    # return as plain HTML (not JSON)
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