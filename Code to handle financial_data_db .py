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

# === Write to SQL table ===
table_name = "macro_indicators_metadata"
df.to_sql(table_name, engine, if_exists="replace", index=False)

# === Add PRIMARY KEY constraint on indicator_code ===
with engine.begin() as conn:
    conn.execute(text(f"""
        ALTER TABLE {table_name}
        ADD PRIMARY KEY (indicator_code);
    """))

print(f"✅ Successfully imported {len(df)} rows into table '{table_name}' with 'indicator_code' as PRIMARY KEY.")
