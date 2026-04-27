from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from packages.metora.engines.base import BaseEngine
from packages.metora.providers.outbox.protocol import OutboxProviderProtocol, OutboxEventProtocol
from packages.metora.providers.stream.protocol import StreamProviderProtocol


class OutboxEngine(BaseEngine):
    """
    OutboxEngine：事件发件箱引擎。

    核心职责：
        1. 创建业务事件记录
        2. 查询待发布事件
        3. 发布事件到 StreamProvider
        4. 追踪发布状态
        5. 失败后支持重试

    不负责：
        - 业务状态修改
        - 通知具体发送
        - WebSocket 推送
        - 事件消费后的业务处理
    """

    engine_name = "outbox"

    def __init__(
        self,
        outbox_provider: OutboxProviderProtocol | None = None,
        stream_provider: StreamProviderProtocol | None = None,
        outbox_provider_name: str = "default",
        stream_provider_name: str = "default",
        registry=None,
    ):
        super().__init__(registry=registry)
        self.outbox_provider = outbox_provider
        self.stream_provider = stream_provider
        self.outbox_provider_name = outbox_provider_name
        self.stream_provider_name = stream_provider_name

    def get_outbox_provider(self) -> OutboxProviderProtocol:
        if self.outbox_provider:
            return self.outbox_provider

        if not self.registry:
            raise RuntimeError("OutboxEngine requires outbox_provider or registry")

        return self.registry.get_provider(
            capability="outbox",
            name=self.outbox_provider_name,
        )

    def get_stream_provider(self) -> StreamProviderProtocol:
        if self.stream_provider:
            return self.stream_provider

        if not self.registry:
            raise RuntimeError("OutboxEngine requires stream_provider or registry")

        return self.registry.get_provider(
            capability="stream",
            name=self.stream_provider_name,
        )

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
        """
        创建事件记录。

        一般在 UseCase 的事务中调用。
        """

        return self.get_outbox_provider().create_event(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            topic=topic,
            key=key,
            payload=payload or {},
            headers=headers or {},
            max_retry_count=max_retry_count,
        )

    def get_event(
        self,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        """
        获取事件记录。
        """

        return self.get_outbox_provider().get_event(event_id)

    def list_pending(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxEventProtocol]:
        """
        查询待发布事件。
        """

        return self.get_outbox_provider().list_pending(
            limit=limit,
        )

    def publish_event(
        self,
        *,
        event_id: str | int,
    ) -> OutboxEventProtocol:
        """
        发布单个事件。

        流程：
            1. 标记 publishing
            2. 调用 StreamProvider.publish()
            3. 成功则标记 published
            4. 失败则标记 pending / failed
        """

        outbox_provider = self.get_outbox_provider()
        stream_provider = self.get_stream_provider()

        event = outbox_provider.mark_publishing(
            event_id=event_id,
        )

        try:
            stream_provider.publish(
                topic=event.topic,
                key=event.key,
                message={
                    "id": event.id,
                    "type": event.event_type,
                    "aggregateType": event.aggregate_type,
                    "aggregateId": event.aggregate_id,
                    "payload": event.payload,
                    "createdAt": event.created_at.isoformat()
                    if event.created_at
                    else None,
                },
                headers=event.headers,
            )

            return outbox_provider.mark_published(
                event_id=event.id,
            )

        except Exception as error:
            next_retry_at = self._calculate_next_retry_at(event)

            return outbox_provider.mark_failed(
                event_id=event.id,
                error=str(error),
                next_retry_at=next_retry_at,
            )

    def publish_pending(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxEventProtocol]:
        """
        发布一批待发布事件。

        一般由后台 Worker 定时调用。
        """

        events = self.list_pending(limit=limit)

        results: list[OutboxEventProtocol] = []

        for event in events:
            result = self.publish_event(event_id=event.id)
            results.append(result)

        return results

    def cancel(
        self,
        *,
        event_id: str | int,
        reason: str | None = None,
    ) -> OutboxEventProtocol:
        """
        取消事件发布。
        """

        return self.get_outbox_provider().cancel(
            event_id=event_id,
            reason=reason,
        )

    def _calculate_next_retry_at(
        self,
        event: OutboxEventProtocol,
    ) -> datetime:
        """
        简单重试策略。

        第 1 次失败：30 秒后
        第 2 次失败：60 秒后
        第 3 次失败：90 秒后
        """

        seconds = 30 * (event.retry_count + 1)

        return datetime.now() + timedelta(seconds=seconds)
