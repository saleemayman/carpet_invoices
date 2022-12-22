from abc import abstractmethod
from dataclasses import dataclass

from definitions.common import SourceTypes, SourceNames


@dataclass
class BaseIngestor:
    source_type: SourceTypes
    source_name: SourceNames

    @abstractmethod
    def add_source_metadata():
        pass

    @abstractmethod
    def insert_into_db():
        pass
