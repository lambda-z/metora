from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from packages.metora.providers.base import ProviderResult


@dataclass
class NotificationMessage:
    receiver: str
    title: str
    content: str
    data: dict[str, Any] = field(default_factory=dict)


class NotificationProviderProtocol(Protocol):
    capability = "notification"

    def send(self, message: NotificationMessage) -> ProviderResult:
        raise NotImplementedError
