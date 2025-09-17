import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

try:
    engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
    )

    df = pd.read_sql_table('bank_customers', engine)
    df['term_deposit'] = df['term_deposit'].map({'yes': 1, 'no': 0})

    agg_df = df.groupby(['job', 'marital', 'education']).agg(
        avg_balance=('balance', 'mean'),
        term_deposit_success_rate=('term_deposit', 'mean'),
        avg_campaign_duration=('duration', 'mean')
    ).reset_index()

    agg_df.to_sql('agg_marketing_insights', engine, if_exists='replace', index=False)
    
    print(f"Successfully aggregated {len(agg_df)} demographic segments into 'agg_marketing_insights'.")

except Exception as e:
    print(f"An error occurred: {e}")
