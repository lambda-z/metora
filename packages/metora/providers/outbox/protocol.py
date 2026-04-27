from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class OutboxEventProtocol(Protocol):
    id: str | int

    event_type: str
    aggregate_type: str
    aggregate_id: str | int | None

    topic: str
    key: str | None
    payload: dict[str, Any]
    headers: dict[str, Any]

    status: str
    retry_count: int
    max_retry_count: int

    last_error: str | None
    next_retry_at: datetime | None

    created_at: datetime | None
    updated_at: datetime | None
    published_at: datetime | None


@dataclass
class OutboxEvent:
    """
    Outbox 事件记录。

    它表示一个需要发布到 Stream / Worker / 外部系统的业务事件。
    """

    id: str | int

    event_type: str
    aggregate_type: str
    aggregate_id: str | int | None = None

    topic: str = "metora.events"
    key: str | None = None

    payload: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, Any] = field(default_factory=dict)

    status: str = "pending"

    retry_count: int = 0
    max_retry_count: int = 3

    last_error: str | None = None
    next_retry_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None


class OutboxProviderProtocol(Protocol):
    """
    OutboxProvider 协议。

    OutboxEngine 不直接依赖数据库，只依赖这个协议。

    具体实现可以是：
        - MemoryOutboxProvider
        - DjangoOutboxProvider
        - SQLAlchemyOutboxProvider
        - BeanieOutboxProvider
    """

    name: str
    capability: str

    def create_event(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str | int | None = None,
        topic: str = "metora.events",
        key: str | None = None,
        payload: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        max_retry_count: int = 3,
    ) -> OutboxEventProtocol:
        ...

    def get_event(
        self,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        ...

    def list_pending(
        self,
        *,
        limit: int = 100,
        now: datetime | None = None,
    ) -> list[OutboxEventProtocol]:
        ...

    def mark_publishing(
        self,
        *,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        ...

    def mark_published(
        self,
        *,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        ...

    def mark_failed(
        self,
        *,
        event_id: str | int,
        error: str,
        next_retry_at: datetime | None = None,
    ) -> OutboxEventProtocol:
        ...

    def cancel(
        self,
        *,
        event_id: str | int,
        reason: str | None = None,
    ) -> OutboxEventProtocol:
        ...
