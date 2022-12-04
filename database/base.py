import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_PORT = os.environ["DB_PORT"] or 5432
DB_HOST = os.environ["DB_HOST"] or "postgres"
DB_USER = os.environ["POSTGRES_USER"] or "postgres"
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"] or "postgres"
DB_NAME = os.environ["POSTGRES_DB"] or "postgres"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True
)

# TODO: check what scoped sessions are used for.
db_session = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=False)
)

Base = declarative_base()
