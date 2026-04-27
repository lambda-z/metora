from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from packages.metora.providers.outbox.protocol import OutboxProviderProtocol, OutboxEvent, OutboxEventProtocol


class MemoryOutboxProvider(OutboxProviderProtocol):
    """
    内存版 OutboxProvider。

    适合：
        - Demo
        - 单元测试
        - 本地快速验证

    注意：
        程序重启后数据会丢失。
    """

    name = "memory"
    capability = "outbox"

    def __init__(self):
        self.events: dict[str | int, OutboxEvent] = {}

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
        now = datetime.now()
        event_id = str(uuid4())

        event = OutboxEvent(
            id=event_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            topic=topic,
            key=key,
            payload=payload or {},
            headers=headers or {},
            status="pending",
            retry_count=0,
            max_retry_count=max_retry_count,
            created_at=now,
            updated_at=now,
        )

        self.events[event_id] = event

        return event

    def get_event(
        self,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        event_id = str(event_id)

        if event_id not in self.events:
            raise KeyError(f"Outbox event not found: {event_id}")

        return self.events[event_id]

    def list_pending(
        self,
        *,
        limit: int = 100,
        now: datetime | None = None,
    ) -> list[OutboxEventProtocol]:
        now = now or datetime.now()

        candidates = [
            event
            for event in self.events.values()
            if event.status in ["pending", "failed"]
            and event.retry_count < event.max_retry_count
            and (
                event.next_retry_at is None
                or event.next_retry_at <= now
            )
        ]

        candidates = sorted(
            candidates,
            key=lambda item: item.created_at or datetime.min,
        )

        return candidates[:limit]

    def mark_publishing(
        self,
        *,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        event = self.get_event(event_id)

        event.status = "publishing"
        event.updated_at = datetime.now()

        return event

    def mark_published(
        self,
        *,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        event = self.get_event(event_id)

        now = datetime.now()

        event.status = "published"
        event.updated_at = now
        event.published_at = now
        event.last_error = None
        event.next_retry_at = None

        return event

    def mark_failed(
        self,
        *,
        event_id: str | int,
        error: str,
        next_retry_at: datetime | None = None,
    ) -> OutboxEventProtocol:
        event = self.get_event(event_id)

        event.retry_count += 1
        event.last_error = error
        event.updated_at = datetime.now()

        if event.retry_count >= event.max_retry_count:
            event.status = "failed"
            event.next_retry_at = None
        else:
            event.status = "pending"
            event.next_retry_at = next_retry_at or (
                datetime.now() + timedelta(seconds=30 * event.retry_count)
            )

        return event

    def cancel(
        self,
        *,
        event_id: str | int,
        reason: str | None = None,
    ) -> OutboxEventProtocol:
        event = self.get_event(event_id)

        event.status = "cancelled"
        event.last_error = reason
        event.updated_at = datetime.now()

        return event
