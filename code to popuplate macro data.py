import os
import pandas as pd
from sqlalchemy import create_engine, text

# === Connection details ===
user = "postgres"
password = "Sami1234"
host = "localhost"
port = "5432"
database = "financial_data_db"

# === Connect to PostgreSQL ===
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

# === Define file paths ===
files = [
    r"C:\Users\bouzi\Documents\finance_database\raw\macro\raw_money_market_rates.csv",
    r"C:\Users\bouzi\Documents\finance_database\raw\macro\raw_policy_rates.csv"
]

# === Prepare SQL table name ===
table_name = "macro_indicators_values"

# === Create the table if it doesn't exist ===
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    indicator_code VARCHAR(50) REFERENCES macro_indicators_metadata(indicator_code) ON DELETE CASCADE,
    date DATE NOT NULL,
    value NUMERIC,
    UNIQUE (indicator_code, date)
);
"""
with engine.begin() as conn:
    conn.execute(text(f"TRUNCATE TABLE {table_name};"))
    

# === Iterate through all files ===
for file_path in files:
    print(f"Processing {file_path}...")

    # Load CSV and normalize headers
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # Try to locate the 'date' column automatically (in case of case/space differences)
    date_col = None
    for c in df.columns:
        if c.strip().lower() == "date":
            date_col = c
            break

    if not date_col:
        raise ValueError(f"'date' column not found in {file_path}. Columns are: {df.columns.tolist()}")

    # Melt to long format
    df_long = df.melt(id_vars=date_col, var_name="indicator_code", value_name="value")
    df_long.rename(columns={date_col: "date"}, inplace=True)

    # Convert and clean
    df_long["date"] = pd.to_datetime(df_long["date"], errors="coerce")
    df_long = df_long.dropna(subset=["date", "indicator_code", "value"])

    # Append to SQL
    df_long.to_sql(table_name, engine, if_exists="append", index=False)

    print(f"Inserted {len(df_long)} rows from {os.path.basename(file_path)}")

print("All raw macro files loaded successfully.")