# from sqlalchemy.schema import CreateSchema, DropSchema
from database.base import engine
from database.base import Base
from definitions.schemas import Schemas
from definitions.source_tables import SourceTables  # noqa


def drop_and_create_all_schemas():
    """
    Drops all schemas as defined in Schemas Enum and recreates them fresh.
    """
    for schema in Schemas:
        print(f"Dropping schema: {schema}")
        with engine.connect() as conn:
            conn.execute(f"DROP SCHEMA IF EXISTS {schema.value} CASCADE;")

    for schema in Schemas:
        print(f"Creating schema: {schema}")
        with engine.connect() as conn:
            conn.execute(f"CREATE SCHEMA {schema.value};")


def init_db():
    drop_and_create_all_schemas()

    # create all tables
    Base.metadata.create_all(
        bind=engine,
    )
