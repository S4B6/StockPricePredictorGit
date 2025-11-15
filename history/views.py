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
    Optionally a 'series' column like 'indicator_code' for colors.
    """

    # Try to detect a "series" column for multiple lines
    color_col = None
    for candidate in ["indicator_code", "series", "name", "label"]:
        if candidate in df.columns:
            color_col = candidate
            break

    # ---- 1) Base figure by type ----
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
            fig = px.line(
                df,
                x="date",
                y="value",
                line_shape="hv",
            )
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

    # Remove legend title
    fig.update_layout(legend_title_text="")

    # ---- 2) Universal styling (copied from your ECB chart) ----
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d0017",
        plot_bgcolor="#0d0017",
        font=dict(family="Courier Prime", color="#ffffff", size=13),

        title=None,  # 👈 remove plotly title

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

        margin=dict(l=40, r=40, t=40, b=40),  # reduced because title is gone
        height=420,
        hovermode="x unified",

        xaxis_hoverformat="%d %b %Y"  # <-- show day-month-year once on top
    )

    # ---- 3) Line style & hover style ----
    fig.update_traces(
        line=dict(width=2.5),
        mode="lines+markers",
        marker=dict(size=4, opacity=0),
        hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}%<extra></extra>"
    )

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