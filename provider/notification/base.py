from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from provider.base import AdapterBase, AdapterResult


@dataclass
class NotificationMessage:
    receiver: str
    title: str
    content: str
    data: dict[str, Any] = field(default_factory=dict)


class NotificationAdapterBase(AdapterBase):
    capability = "notification"

    @abstractmethod
    def send(self, message: NotificationMessage) -> AdapterResult:
        raise NotImplementedError
