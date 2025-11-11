import pandas as pd
import plotly.express as px
from django.shortcuts import render
from sqlalchemy import create_engine

def history_index(request):
    engine = create_engine("postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db")

    query = """
        SELECT * 
        FROM macro_indicators_values 
        WHERE indicator_code IN ('ECB_DF','ECB_MRO','ECB_MLF','ESTER')
        ORDER BY date
    """
    df = pd.read_sql(query, engine)

    fig = px.line(
        df,
        x="date",
        y="value",
        color="indicator_code",
        title="ECB Policy & Money Market Rates (since 1999)",
        line_shape="hv"
    )

    fig.update_layout(template="plotly_white", height=600)

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return render(request, "history/index.html", {"chart": chart_html})