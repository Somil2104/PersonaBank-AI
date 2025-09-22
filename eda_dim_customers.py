import os, pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
eng = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

df = pd.read_sql_table('dim_customers', eng)

print("Rows:", len(df))
print(df[['account_age_days','days_since_last_transaction']].describe())

print("Nulls:")
print(df[['customer_id','date_of_account_opening','last_transaction_date']].isna().sum())

print("Balances (head/tail):")
print(df[['account_balance']].describe())

print("Top cities by count:")
print(df['city'].value_counts().head(10))

print("Loan status distribution:")
if 'loan_status' in df.columns:
    print(df['loan_status'].value_counts(dropna=False))
