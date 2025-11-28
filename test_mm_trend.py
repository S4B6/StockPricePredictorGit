import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

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

df = pd.read_sql(sql, engine)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["indicator_code", "date"])
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["value"])

pivot = df.pivot(index="date", columns="indicator_code", values="value")
pivot = pivot.sort_index()

# ------------------------------------------------------------
# 2) MERGE EONIA + ESTER (simply sum them)
# ------------------------------------------------------------
if "EONIA" in pivot.columns and "ESTER" in pivot.columns:
    pivot["EURO_ON"] = pivot["EONIA"].fillna(0) + pivot["ESTER"].fillna(0)
    pivot["EURO_ON"].replace(0, np.nan, inplace=True)
    pivot.drop(columns=["EONIA", "ESTER"], inplace=True)

# ------------------------------------------------------------
# 3) BUILD BALANCED PANEL FOR PCA (best practice)
# ------------------------------------------------------------
pivot_pca = pivot.dropna()      # NO interpolation → real consistent panel

# ------------------------------------------------------------
# EXPORT PCA DATASET FOR VERIFICATION
# ------------------------------------------------------------
pivot_pca.to_csv("pca_input_dataset.csv")
print("\nExported PCA input dataset.")

# ------------------------------------------------------------
# 4) STANDARDIZE
# ------------------------------------------------------------
X = (pivot_pca - pivot_pca.mean()) / pivot_pca.std()

# ------------------------------------------------------------
# 5) PCA
# ------------------------------------------------------------
pca = PCA(n_components=1)
PC1 = pca.fit_transform(X)
PC1_series = pd.Series(PC1.flatten(), index=X.index, name="PC1")

print("\nVariance explained by global factor:", 
      round(pca.explained_variance_ratio_[0] * 100, 2), "%")

# ------------------------------------------------------------
# 6) REGRESS EACH CB ON PC1 → β & R²
# ------------------------------------------------------------
betas, r2s = {}, {}

for col in X.columns:
    y = X[col].values.reshape(-1, 1)
    model = LinearRegression().fit(PC1, y)
    betas[col] = model.coef_[0][0]
    r2s[col]   = model.score(PC1, y)

results = pd.DataFrame({
    "beta_loading": betas,
    "R2_explained": r2s
}).sort_values("R2_explained", ascending=False)

print("\n=== Global-Monetary-Factor Results ===")
print(results)

# ------------------------------------------------------------
# 7) CORRELATION-BASED MONEY MARKET MAP (bubble chart)
# ------------------------------------------------------------
means = pivot.mean()
stds = pivot.std()

corr = pivot.corr()

# Correct average correlation (exclude self)
avg_corr = corr.apply(lambda row: row.drop(row.name).mean(), axis=1)
avg_abs_corr = corr.apply(lambda row: row.drop(row.name).abs().mean(), axis=1)

# ------------------------------------------------------------
# EXPORT BUBBLE CHART DATA
# ------------------------------------------------------------
summary_df = pd.DataFrame({
    "mean": means,
    "std": stds,
    "avg_corr": avg_corr,
    "avg_abs_corr": avg_abs_corr
})
summary_df.to_csv("bubblechart_summary_stats.csv")
corr.to_csv("bubblechart_correlation_matrix.csv")
pivot.to_csv("bubblechart_raw_timeseries.csv")
print("\nExported bubble-chart datasets.")

# ------------------------------------------------------------
# 8) PLOT BUBBLE CHART
# ------------------------------------------------------------
plt.figure(figsize=(14, 10))

scatter = plt.scatter(
    means,
    stds,
    s=avg_abs_corr * 2500,   # bubble size
    c=avg_corr,              # bubble color = avg corr
    cmap="coolwarm",
    alpha=0.85,
    edgecolor="black",
    linewidth=0.7
)

for code in pivot.columns:
    plt.text(
        means[code],
        stds[code],
        code,
        fontsize=8,
        ha="center",
        va="center"
    )

plt.xlabel("Average Level (%)")
plt.ylabel("Volatility (Std Dev)")
plt.title("Money-Market Structure Map\n(mean → x, volatility → y, correlation → size & color)")

cbar = plt.colorbar(scatter)
cbar.set_label("Average Correlation with Others")

plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()
