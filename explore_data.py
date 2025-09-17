import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

try:
    engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
    )
    inspector = inspect(engine)

    table_names = [
        'bank_customers',
        'bank_marketing_additional',
        'comprehensive_banking_data',
        'paysim_transactions'
    ]

    for table in table_names:
        if inspector.has_table(table):
            print(f"\n--- Schema: {table} ---")
            for col in inspector.get_columns(table):
                print(f"  {col['name']} ({col['type']})")
        else:
            print(f"\nWarning: Table '{table}' not found.")

except Exception as e:
    print(f"An error occurred: {e}")
