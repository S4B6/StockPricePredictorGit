import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db"
)

sql = """
SELECT
    v.date,
    v.value,
    m.indicator_code,
    m.institution
FROM macro_indicators_values v
JOIN macro_indicators_metadata m USING (indicator_code)
WHERE m.indicator_type = 'money market rate'
ORDER BY v.date;
"""

df = pd.read_sql(sql, engine)
df['date'] = pd.to_datetime(df['date'])

# ----------------------------
# 1) Extract China FR001
# ----------------------------
df_china = df[df["indicator_code"] == "CHINA_FR001"].copy()

# Monthly smoothing
china_monthly = (
    df_china.set_index("date")["value"]
             .resample("ME")
             .mean()
)

# Convert monthly to daily
china_daily_smoothed = (
    china_monthly
        .resample("D")
        .ffill()
        .reset_index()
        .rename(columns={"value": "value"})
)

# Add metadata back
china_daily_smoothed["indicator_code"] = "CHINA_FR001_SMOOTH"
china_daily_smoothed["institution"] = "PBOC"

# ----------------------------
# 2) All other MM rates unchanged
# ----------------------------
df_other = df[df["indicator_code"] != "CHINA_FR001"].copy()

# ----------------------------
# 3) Combine final dataframe
# ----------------------------
df_final = pd.concat([df_other, china_daily_smoothed], ignore_index=True)
df_final = df_final.sort_values("date")

# ----------------------------
# 4) Plot
# ----------------------------
import plotly.express as px

fig = px.line(
    df_final,
    x="date",
    y="value",
    color="indicator_code",
    title="All Money-Market Rates (China Smoothed Monthly)",
)

fig.update_layout(
    template="plotly_dark",
    height=650,
    legend=dict(orientation="h", y=-0.25)
)

fig.show()
