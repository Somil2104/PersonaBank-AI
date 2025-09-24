import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

conn_str = "postgresql://{user}:{pwd}@localhost:5432/{db}".format(
    user=os.getenv("POSTGRES_USER"),
    pwd=os.getenv("POSTGRES_PASSWORD"),
    db=os.getenv("POSTGRES_DB"),
)
engine = create_engine(conn_str)

# Discover actual one-hot columns
probe = pd.read_sql_query("SELECT * FROM paysim_features LIMIT 1", engine)
type_cols = [c for c in probe.columns if c.lower().startswith("type_")]

# Build SELECT list safely
base_cols = [
    "step",
    "isfraud",
    "amount",
    "amount_to_oldbalanceorg",
    "amount_to_oldbalancedest",
    "delta_origin",
    "delta_dest",
]
select_cols = base_cols + type_cols
quoted = ", ".join(['"' + c + '"' for c in select_cols])
sql = "SELECT " + quoted + " FROM paysim_features"

# Fetch, split, save
df = pd.read_sql_query(sql, engine)
split_step = 400
train = df[df["step"] <= split_step].reset_index(drop=True)
test = df[df["step"] > split_step].reset_index(drop=True)

train.to_csv("paysim_train.csv", index=False)
test.to_csv("paysim_test.csv", index=False)

print("Export complete.")
print(" - paysim_train.csv:", len(train))
print(" - paysim_test.csv:", len(test))
print("Type columns used:", type_cols)
