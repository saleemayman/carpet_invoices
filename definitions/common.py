from enum import Enum


class SourceTypes(Enum):
    csv = "csv"
    pdf = "pdf"


class SourceNames(Enum):
    amazon_aws = "amazon_aws"
    carpets_external = "carpets_external"
