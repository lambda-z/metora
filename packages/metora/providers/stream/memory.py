from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from providers.stream.protocol import StreamProviderProtocol


@dataclass
class MemoryStreamMessage:
    topic: str
    message: dict[str, Any]
    key: str | None = None
    headers: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None


class MemoryStreamProvider(StreamProviderProtocol):
    """
    内存版 StreamProvider。

    适合单元测试和 Demo。
    """

    name = "memory"
    capability = "stream"

    def __init__(self):
        self.messages: list[MemoryStreamMessage] = []

    def publish(
        self,
        *,
        topic: str,
        message: dict[str, Any],
        key: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> None:
        self.messages.append(
            MemoryStreamMessage(
                topic=topic,
                message=message,
                key=key,
                headers=headers or {},
                created_at=datetime.now(),
            )
        )
