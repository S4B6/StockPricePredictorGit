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

# === File path ===
file_path = r"C:\Users\bouzi\Documents\finance_database\exports\export_macro_indicators_meta.csv"

# === Load CSV ===
df = pd.read_csv(file_path, encoding="ISO-8859-1")
print(f"Loaded {len(df)} rows from {file_path}")

table_name = "macro_indicators_metadata"

# === STEP 1: Automatically add missing columns in SQL ===
with engine.begin() as conn:
    # Get existing database columns
    result = conn.execute(text(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}';
    """))
    existing_cols = {row[0] for row in result.fetchall()}

    # Add new columns if they don't exist
    for col in df.columns:
        if col not in existing_cols:
            print(f"⚠️ Adding missing column: {col}")
            conn.execute(text(
                f"ALTER TABLE {table_name} ADD COLUMN {col} TEXT;"
            ))

print("✅ Schema synchronized with CSV.")

# === STEP 2: Delete all existing rows (safe refresh) ===
with engine.begin() as conn:
    conn.execute(text(f"DELETE FROM {table_name};"))

print("🗑️ Cleared existing data.")

# === STEP 3: Insert fresh data ===
df.to_sql(table_name, engine, if_exists="append", index=False)

print(f"📥 Inserted {len(df)} new rows.")
