import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

try:
    engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
    )
    
    print("Extracting from 'comprehensive_banking_data'...")
    df = pd.read_sql_table('comprehensive_banking_data', engine)

    print("Transforming data...")
    df.columns = [col.lower().replace('/', '_').replace(' ', '_') for col in df.columns]
    df.rename(columns={'transactionid': 'transaction_id', 'cardid': 'card_id'}, inplace=True)

    date_columns = [
        'date_of_account_opening', 'last_transaction_date', 'transaction_date',
        'approval_rejection_date', 'payment_due_date', 'last_credit_card_payment_date',
        'feedback_date', 'resolution_date'
    ]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df['account_age_days'] = (pd.to_datetime('now') - df['date_of_account_opening']).dt.days
    df['days_since_last_transaction'] = (pd.to_datetime('now') - df['last_transaction_date']).dt.days

    print("Loading data into 'dim_customers'...")
    df.to_sql('dim_customers', engine, if_exists='replace', index=False)
    
    print(f"Successfully loaded {len(df)} records into 'dim_customers'.")

except Exception as e:
    print(f"An error occurred: {e}")
