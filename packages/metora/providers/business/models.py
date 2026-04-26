# metora/persistence/models/business.py

from typing import Protocol
from packages.metora.core.resources import Resource


class BusinessInstanceProtocol(Protocol):
    id: str | int
    business_type: str
    title: str
    status: str

    def to_resource(self) -> Resource:
        ...
