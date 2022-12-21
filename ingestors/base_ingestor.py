from abc import abstractmethod
from dataclasses import dataclass

from definitions.common import SourceTypes, SourceNames


@dataclass
class BaseIngestor:
    # table_name: str
    source_type: SourceTypes
    source_name: SourceNames

    @abstractmethod
    def add_source_metadata():
        pass
