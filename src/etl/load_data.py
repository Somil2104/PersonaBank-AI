import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = os.getenv('POSTGRES_DB')

DATA_DIR = 'data'
DATA_FILES_TO_TABLES = {
    'BankCustomerdata.csv': 'bank_customers',
    'bank-additional-full.csv': 'bank_marketing_additional',
    'CBD.csv': 'comprehensive_banking_data',
    'PS_20174392719_1491204439457_log.csv': 'paysim_transactions',
}

def main():
    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        print("Error: Database credentials not found in .env file.")
        return

    print("Starting data loading process...")
    try:
        engine = create_engine(
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
        print("Successfully connected to PostgreSQL.")
    except Exception as e:
        print(f"Error: Could not connect to the database. {e}")
        return

    for file_name, table_name in DATA_FILES_TO_TABLES.items():
        file_path = os.path.join(DATA_DIR, file_name)
        
        if os.path.exists(file_path):
            try:
                print(f"Processing '{file_name}'...")
                separator = ';' if 'bank-additional-full' in file_name else ','
                df = pd.read_csv(file_path, sep=separator)
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('.', '_')
                df.to_sql(table_name, engine, if_exists='replace', index=False)
                print(f"-> Loaded {df.shape[0]} rows into '{table_name}'.")
            except Exception as e:
                print(f"-> Error loading {file_name}: {e}")
        else:
            print(f"Warning: File not found at '{file_path}'. Skipping.")

    print("\nData loading complete.")

if __name__ == '__main__':
    main()
