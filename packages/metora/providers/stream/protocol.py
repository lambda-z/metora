from __future__ import annotations

from typing import Any, Protocol


class StreamProviderProtocol(Protocol):
    """
    StreamProvider 负责事件流 / 消息流的发布。

    它可以适配：
        - Kafka
        - Redis Stream
        - RabbitMQ
        - NATS
        - SQS
        - MemoryStreamProvider
    """

    name: str
    capability: str

    def publish(
        self,
        *,
        topic: str,
        message: dict[str, Any],
        key: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> None:
        """
        发布一条消息。
        """
        ...
