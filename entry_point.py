from database.base import db_session
from database.db import init_db
from definitions.data_ingestors import SourceDataIngestors

init_db()

for ingestor in SourceDataIngestors:
    ingestor_instance = ingestor.value()
    ingestor_instance.add_source_metadata()
    ingestor_instance.insert_into_db()

db_session.commit()
