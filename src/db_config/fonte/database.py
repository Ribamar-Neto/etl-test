from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USERNAME = getenv("DB_USERNAME", "postgres")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = getenv("DB_PORT")
SOURCE_DATABASE = getenv("SOURCE_DATABASE")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{SOURCE_DATABASE}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
