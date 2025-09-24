import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
def get_engine():
    host = os.getenv("POSTGRES_HOST","localhost")
    port = int(os.getenv("POSTGRES_PORT","5432"))
    user = os.getenv("POSTGRES_USER")
    pwd  = os.getenv("POSTGRES_PASSWORD")
    db   = os.getenv("POSTGRES_DB")
    return create_engine(f"postgresql://{user}:{pwd}@{host}:{port}/{db}")
