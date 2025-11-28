import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1) LOAD DATA
# ------------------------------------------------------------
engine = create_engine(
    "postgresql+psycopg2://postgres:Sami1234@localhost:5432/financial_data_db"
)

sql = """
SELECT
    v.date,
    v.value,
    m.indicator_code
FROM macro_indicators_values v
JOIN macro_indicators_metadata m USING (indicator_code)
WHERE m.indicator_type = 'money market rate'
ORDER BY v.date;
"""

print("Loading SQL data...")
df = pd.read_sql(sql, engine)      # <--- df is created HERE
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(["indicator_code", "date"])

df['value'] = pd.to_numeric(df['value'], errors='coerce')
df = df.dropna(subset=['value'])
df = df.sort_values(['indicator_code','date'])


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ----------------------------------------------------------
# PREP
# ----------------------------------------------------------
pivot = df.pivot(index='date', columns='indicator_code', values='value')
pivot = pivot.sort_index()
pivot = pivot.interpolate()

years = pivot.index.year.unique()
last_full_year = years[-2]
current_year = years[-1]

# YEARLY (all years except last full year/current year)
yearly = pivot[pivot.index.year < last_full_year].resample("Y").mean()
yearly.index = yearly.index.year.astype(str)

# QUARTERLY (last full year)
quarterly = pivot[pivot.index.year == last_full_year].resample("Q").mean()
quarterly.index = quarterly.index.to_period("Q").astype(str)

# MONTHLY (current year)
monthly = pivot[pivot.index.year == current_year].resample("M").mean()
monthly.index = monthly.index.to_period("M").astype(str)

# Combined
combined = pd.concat([yearly, quarterly, monthly])
combined = combined.T


global_mm = pivot.mean(axis=1)
dispersion = pivot.std(axis=1)


# Prepare min, max, last
min_vals = pivot.min()
max_vals = pivot.max()
last_vals = pivot.iloc[-1]


fig = plt.figure(figsize=(26, 18))
gs = GridSpec(6, 4, figure=fig, wspace=0.4, hspace=1.2)


# ---------------- PANEL 1A – Global composite ----------------
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(global_mm.index, global_mm, color="black", linewidth=2)
ax1.set_title("Global Money Market Composite (Average of All Rates)")
ax1.grid(True, linestyle='--', alpha=0.3)

# ---------------- PANEL 1B – Dispersion ----------------
ax2 = fig.add_subplot(gs[1, :])
ax2.plot(dispersion.index, dispersion, color="purple", linewidth=2)
ax2.set_title("Dispersion Index (Cross-Sectional Volatility of MM Rates)")
ax2.grid(True, linestyle='--', alpha=0.3)



ax3 = fig.add_subplot(gs[2:5, :3])
im = ax3.imshow(combined, aspect='auto', cmap='turbo')

plt.colorbar(im, ax=ax3, fraction=0.02)
ax3.set_title("Money Market Rates (Yearly → Quarterly → Monthly)")

ax3.set_xticks(np.arange(len(combined.columns)))
ax3.set_xticklabels(combined.columns, rotation=45, fontsize=8)

ax3.set_yticks(np.arange(len(combined.index)))
ax3.set_yticklabels(combined.index, fontsize=9)

# Shaded regime bands
regimes = [
    ("2008 GFC", "2007", "2009"),
    ("Euro Crisis", "2011", "2013"),
    ("COVID", "2020", "2021"),
    ("Inflation Shock", "2022", "2023")
]

dates_list = list(combined.columns)

for name, start, end in regimes:
    if start in dates_list and end in dates_list:
        i1 = dates_list.index(start)
        i2 = dates_list.index(end)
        ax3.axvspan(i1, i2, color="grey", alpha=0.15)



ax4 = fig.add_subplot(gs[2:5, 3])

ax4.set_title("Sparklines (Long-Term Trend)")
ax4.axis('off')

y_positions = np.linspace(0.95, 0.05, len(pivot.columns))

for y, code in zip(y_positions, pivot.columns):
    series = pivot[code].dropna()
    norm = (series - series.min()) / (series.max() - series.min() + 1e-9)
    ax4.plot(norm.index, norm.values, linewidth=1)
    ax4.text(series.index[-1], norm.values[-1], f"  {code}", va="center", fontsize=8)

ax4.set_ylim(0, 1)


ax5 = fig.add_subplot(gs[5, :])

ax5.set_title("Range Bars (min → current → max)")
ax5.set_xlim(0, 1)
ax5.set_ylim(0, len(pivot.columns)+1)
ax5.set_yticks(range(1, len(pivot.columns)+1))
ax5.set_yticklabels(pivot.columns)

for i, code in enumerate(pivot.columns, start=1):
    mn, mx, cur = min_vals[code], max_vals[code], last_vals[code]
    ax5.hlines(i, 0.1, 0.9, color="grey", alpha=0.4)
    pos = 0.1 + 0.8 * ((cur - mn) / (mx - mn + 1e-9))
    ax5.plot(pos, i, 'o', color="black")
    ax5.text(0.92, i, f"{cur:.2f}", va="center")

fig.suptitle("Global Money Market Dashboard (Enriched)", fontsize=20)
plt.show()
