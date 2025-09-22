import os, pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
eng = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

q = "SELECT step, isfraud, amount, amount_to_oldbalanceorg, amount_to_oldbalancedest, delta_origin, delta_dest, \
            type_CASH_IN, type_CASH_OUT, type_DEBIT, type_PAYMENT, type_TRANSFER \
     FROM paysim_features"
df = pd.read_sql_query(q, eng)

split_step = 400
train = df[df['step'] <= split_step].reset_index(drop=True)
test  = df[df['step'] >  split_step].reset_index(drop=True)

os.makedirs('data/processed', exist_ok=True)
train.to_parquet('data/processed/paysim_train.parquet', index=False)
test.to_parquet('data/processed/paysim_test.parquet', index=False)

print(len(train), len(test))
