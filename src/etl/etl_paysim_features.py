import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
eng = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

df = pd.read_sql_table('paysim_transactions', eng)

required = ['amount','oldbalanceorg','newbalanceorig','oldbalancedest','newbalancedest','type','isfraud']
missing = [c for c in required if c not in df.columns]
if missing:
    raise RuntimeError(f"Missing columns: {missing}")

df['amount_to_oldbalanceorg'] = df['amount'] / df['oldbalanceorg'].replace(0, pd.NA)
df['amount_to_oldbalancedest'] = df['amount'] / df['oldbalancedest'].replace(0, pd.NA)
df['delta_origin'] = df['newbalanceorig'] - df['oldbalanceorg']
df['delta_dest'] = df['newbalancedest'] - df['oldbalancedest']
df = pd.get_dummies(df, columns=['type'], prefix='type', dtype=int)

df.to_sql('paysim_features', eng, if_exists='replace', index=False, chunksize=200000, method='multi')
print(len(df))
