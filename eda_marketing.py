import os, pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
eng = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

df = pd.read_sql_table('agg_marketing_insights', eng)

print("Rows:", len(df))
print("Top segments by term deposit success:")
print(df.sort_values('term_deposit_success_rate', ascending=False).head(10))

print("Correlation overview:")
print(df[['avg_balance','avg_campaign_duration','term_deposit_success_rate']].corr())
