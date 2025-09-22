import os, pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
eng = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

q = "SELECT isfraud, amount, oldbalanceorg, newbalanceorig, oldbalancedest, newbalancedest, amount_to_oldbalanceorg, amount_to_oldbalancedest, delta_origin, delta_dest FROM paysim_features LIMIT 100000"
df = pd.read_sql_query(q, eng)

print("Rows sampled:", len(df))
print("Fraud rate:", df['isfraud'].mean())

print("Feature stats:")
print(df[['amount','amount_to_oldbalanceorg','amount_to_oldbalancedest','delta_origin','delta_dest']].describe())

print("Nulls:")
print(df.isna().sum().sort_values(ascending=False).head(10))
