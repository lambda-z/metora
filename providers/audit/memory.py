from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from core.context import RequestContext
from core.resources import Resource
from providers.audit.protocol import (
    AuditProviderProtocol,
    AuditRecord,
    AuditRecordProtocol,
)


class MemoryAuditProvider(AuditProviderProtocol):
    """
    内存版 AuditProvider。

    适合：
        - 单元测试
        - Demo
        - 本地快速验证

    注意：
        数据只存在内存中，程序重启后会丢失。
    """

    name = "memory"
    capability = "audit"

    def __init__(self):
        self.records: list[AuditRecord] = []

    def record(
        self,
        *,
        context: RequestContext,
        action: str,
        resource: Resource,
        result: str = "success",
        message: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditRecordProtocol:
        record = AuditRecord(
            id=str(uuid4()),

            actor_id=context.actor_id,
            action=action,

            resource_type=resource.type,
            resource_id=resource.id,

            business_id=context.business_id or resource.business_id,
            business_type=context.business_type or resource.business_type,

            result=result,
            message=message,

            before=before or {},
            after=after or {},
            metadata=metadata or {},

            trace_id=context.trace_id,
            request_id=context.request_id,
            source=context.source,

            created_at=datetime.now(),
        )

        self.records.append(record)

        return record

    def list_by_resource(
        self,
        *,
        resource_type: str,
        resource_id: str | int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[AuditRecordProtocol]:
        matched = [
            record
            for record in self.records
            if record.resource_type == resource_type
            and str(record.resource_id) == str(resource_id)
        ]

        matched = sorted(
            matched,
            key=lambda item: item.created_at or datetime.min,
            reverse=True,
        )

        return matched[offset: offset + limit]

    def list_by_actor(
        self,
        *,
        actor_id: str | int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[AuditRecordProtocol]:
        matched = [
            record
            for record in self.records
            if str(record.actor_id) == str(actor_id)
        ]

        matched = sorted(
            matched,
            key=lambda item: item.created_at or datetime.min,
            reverse=True,
        )

        return matched[offset: offset + limit]
