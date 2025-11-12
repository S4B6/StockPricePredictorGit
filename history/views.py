import pandas as pd
import plotly.express as px
from django.shortcuts import render
from sqlalchemy import create_engine
from django.http import HttpResponse
import io

def history_category(request, category):
    return render(request, "history/category.html", {"category": category.capitalize()})

def history(request):
    engine = create_engine("postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db")

    query = """
        SELECT *
        FROM macro_indicators_values
        WHERE indicator_code IN ('ECB_DF', 'ECB_MRO', 'ECB_MLF', 'ESTER')
        ORDER BY date
    """
    df = pd.read_sql(query, engine)

    fig = px.line(
        df,
        x="date",
        y="value",
        color="indicator_code",
        line_shape="hv",
    )

    # remove unwanted legend title
    fig.update_layout(legend_title_text="")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d0017",      # match site background
        plot_bgcolor="#0d0017",
        font=dict(family="Courier Prime", color="#f5f5f5", size=13),

        title=dict(
            text="ECB Policy & Money Market Rates",
            x=0.5,
            xanchor="center",
            font=dict(size=20, color="#ffffff")
        ),

        xaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#d1d1d1"),
        ),
        yaxis=dict(
            title="%",
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#d1d1d1"),
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#e0e0e0"),
        ),

        margin=dict(l=40, r=40, t=60, b=40),
        height=420,
    )


    fig.update_traces(line=dict(width=2.5))
    fig.update_traces(selector=dict(name="ECB_MRO"), line=dict(color="#4682B4"))  # bluish
    fig.update_traces(selector=dict(name="ECB_MLF"), line=dict(color="#FF6347"))  # reddish
    fig.update_traces(selector=dict(name="ECB_DF"),  line=dict(color="#00FFDD"))  # bright green
    fig.update_traces(selector=dict(name="ESTER"),   line=dict(color="#F2FF3A"))  # magenta

    fig.update_traces(
        mode="lines+markers",
        marker=dict(size=4, opacity=0),
        hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}%<extra></extra>"
    )

    fig.update_layout(
        hovermode="x unified",  # one shared hover box with one date header
        hoverlabel=dict(
            bgcolor="#1c1c1c",
            bordercolor="#ffffff",
            font_size=12,
            font_family="JetBrains Mono, monospace"
        ),
        xaxis_hoverformat="%d %b %Y"  # <-- show day-month-year once on top
    )

    # Hide toolbar & simplify interactivity
    chart_html = fig.to_html(
        full_html=False,
       include_plotlyjs=False,
        config=dict(
            displayModeBar=False,   # hides toolbar
            scrollZoom=False,       # disable zoom
            staticPlot=False        # allows hover but disables drag/zoom
        )
    )

    return render(request, "history/history.html", {"chart": chart_html})


def download_macro_data(request):
    engine = create_engine("postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db")
    query = """
        SELECT *
        FROM macro_indicators_values
        WHERE indicator_code IN ('ECB_DF', 'ECB_MRO', 'ECB_MLF', 'ESTER')
        ORDER BY date
    """
    df = pd.read_sql(query, engine)

    # Convert DataFrame → CSV (in memory)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Return downloadable file
    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ecb_rates_history.csv"'
    return response