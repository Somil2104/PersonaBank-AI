import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
eng = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

with eng.connect() as c:
    for t in ['bank_customers','bank_marketing_additional','comprehensive_banking_data','paysim_transactions','dim_customers','agg_marketing_insights','paysim_features']:
        try:
            print(t, c.execute(text(f'SELECT COUNT(*) FROM {t}')).scalar())
        except Exception:
            print(t, 'missing')
