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
# 2) MERGE EONIA + ESTER INTO ONE EURO OVERNIGHT SERIES
# ------------------------------------------------------------
def merge_euro_overnight(df, eonia="EONIA", ester="ESTER"):
    merged = pd.Series(index=df.index, dtype=float)

    for date in df.index:
        if date < pd.Timestamp("2019-10-02"):
            merged[date] = df.loc[date, eonia]
        elif date < pd.Timestamp("2022-01-01"):
            merged[date] = df.loc[date, ester] + 0.085  # transition rule
        else:
            merged[date] = df.loc[date, ester]

    return merged.rename("EURO_ON")


pivot["EURO_ON"] = merge_euro_overnight(pivot)

# REMOVE raw EONIA and ESTER to avoid double counting in PCA
for col in ["EONIA", "ESTER"]:
    if col in pivot.columns:
        pivot = pivot.drop(columns=[col])


# ------------------------------------------------------------
# 3) BUILD A BALANCED PANEL FOR PCA (drop rows with NaN)
# ------------------------------------------------------------
pivot_pca = pivot.dropna()      # strict: no interpolation, clean balanced panel


# ------------------------------------------------------------
# 4) STANDARDIZE
# ------------------------------------------------------------
X = (pivot_pca - pivot_pca.mean()) / pivot_pca.std()


# ------------------------------------------------------------
# 5) RUN PCA (extract global factor)
# ------------------------------------------------------------
pca = PCA(n_components=1)
PC1 = pca.fit_transform(X)
PC1_series = pd.Series(PC1.flatten(), index=X.index, name="PC1")

print("Variance explained by global factor (PC1):",
      round(pca.explained_variance_ratio_[0] * 100, 2), "%")


# ------------------------------------------------------------
# 6) REGRESS EACH CB ON PC1 → β and R²
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


# Optional: R² bar chart
results["R2_explained"].plot.bar(
    figsize=(10,4),
    title="Central Bank – % of Movements Explained by Global Monetary Factor (PC1)"
)
plt.show()


# ------------------------------------------------------------
# 7) CORRELATION MATRIX vs PCA
# ------------------------------------------------------------
corr_matrix = pivot_pca.corr()

avg_corr = corr_matrix.apply(lambda row: row.drop(row.name).mean(), axis=1)
avg_corr = avg_corr.rename("average_corr")

comparison = pd.concat([results["R2_explained"], avg_corr], axis=1)
comparison["rank_R2"] = comparison["R2_explained"].rank(ascending=False)
comparison["rank_corr"] = comparison["average_corr"].rank(ascending=False)

comparison = comparison.sort_values("R2_explained", ascending=False)

print("\n=== COMPARISON: PCA R² vs AVERAGE CORRELATION ===")
print(comparison)

comparison["rank_diff"] = comparison["rank_corr"] - comparison["rank_R2"]
print("\n=== Ranking Differences (Corr - PCA_R2) ===")
print(comparison["rank_diff"])


# ------------------------------------------------------------
# EXPORT DATASET USED IN ANALYSIS
# ------------------------------------------------------------
pivot_pca.to_csv("pca_input_dataset.csv", index=True)
print("\nData exported to pca_input_dataset.csv")