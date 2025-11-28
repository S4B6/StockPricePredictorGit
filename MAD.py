import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. LOAD DATA
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

df = pd.read_sql(sql, engine)
df["date"] = pd.to_datetime(df["date"])
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["value"])

# ------------------------------------------------------------
# 2. EXCLUDE COUNTRIES
# ------------------------------------------------------------
EXCLUDE = ["CHINA_FR001", "CALL_RATE"]  # update if needed
df = df[~df["indicator_code"].isin(EXCLUDE)]

# ------------------------------------------------------------
# 3. BUILD PIVOT (with NaN preserved)
# ------------------------------------------------------------
pivot = df.pivot(index="date", columns="indicator_code", values="value")
pivot = pivot.sort_index()
# Daily frequency index (no jumps)
pivot = pivot.asfreq("D")

# Forward-fill short gaps (weekends)
pivot = pivot.ffill(limit=4)

print(pivot)



import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 3 TYPES OF DAILY CROSS-SECTIONAL DISPERSION
# ------------------------------------------------------------

def mad_mean(row):
    """Mean absolute deviation from the mean."""
    vals = row.dropna()
    if len(vals) < 2:
        return np.nan
    mean = vals.mean()
    return np.mean(np.abs(vals - mean))


def mad_median(row):
    """Median absolute deviation from the median (robust MAD)."""
    vals = row.dropna()
    if len(vals) < 2:
        return np.nan
    med = vals.median()
    return np.median(np.abs(vals - med))


def mad_hybrid(row):
    """Hybrid: mean absolute deviation from the median."""
    vals = row.dropna()
    if len(vals) < 2:
        return np.nan
    med = vals.median()
    return np.mean(np.abs(vals - med))


# Compute all 3 series
mad_mean_series   = pivot.apply(mad_mean, axis=1)
mad_median_series = pivot.apply(mad_median, axis=1)
mad_hybrid_series = pivot.apply(mad_hybrid, axis=1)



plt.figure(figsize=(14, 5))
plt.plot(mad_mean_series.index, mad_mean_series.values, color="white", linewidth=2)

plt.title("Cross-Sectional Dispersion — Mean Absolute Deviation", color="white", fontfamily="Courier Prime")
plt.ylabel("MAD-Mean", color="white", fontfamily="Courier Prime")

plt.grid(True, linestyle="--", alpha=0.3)
plt.gca().set_facecolor("#0d0017")
plt.gcf().set_facecolor("#0d0017")
plt.tick_params(colors="white")
plt.show()


plt.figure(figsize=(14, 5))
plt.plot(mad_median_series.index, mad_median_series.values, color="white", linewidth=2)

plt.title("Cross-Sectional Dispersion — Median Absolute Deviation (Robust)", 
          color="white", fontfamily="Courier Prime")
plt.ylabel("MAD-Median", color="white", fontfamily="Courier Prime")

plt.grid(True, linestyle="--", alpha=0.3)
plt.gca().set_facecolor("#0d0017")
plt.gcf().set_facecolor("#0d0017")
plt.tick_params(colors="white")
plt.show()

plt.figure(figsize=(14, 5))
plt.plot(mad_hybrid_series.index, mad_hybrid_series.values, color="white", linewidth=2)

plt.title("Cross-Sectional Dispersion — Hybrid MAD (mean(|x - median|))", 
          color="white", fontfamily="Courier Prime")
plt.ylabel("MAD-Hybrid", color="white", fontfamily="Courier Prime")

plt.grid(True, linestyle="--", alpha=0.3)
plt.gca().set_facecolor("#0d0017")
plt.gcf().set_facecolor("#0d0017")
plt.tick_params(colors="white")
plt.show()
