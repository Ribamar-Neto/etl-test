from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_USERNAME = getenv("DB_USERNAME", "postgres")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = getenv("DB_PORT")
TARGET_DATABASE = getenv("TARGET_DATABASE")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TARGET_DATABASE}"

engine_for_target_db = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_for_target_db)

Base = declarative_base()
