import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

username = os.getenv("DB_username")
raw_password = os.getenv("DB_password")
password = quote_plus(raw_password) 
host = os.getenv("DB_host")
port = int(os.getenv("DB_port"))
database = os.getenv("DB_database")

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
