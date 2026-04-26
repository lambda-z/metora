from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from core.context import RequestContext
from core.resources import Resource


@runtime_checkable
class AuditRecordProtocol(Protocol):
    id: str | int

    actor_id: str | int | None
    action: str

    resource_type: str
    resource_id: str | int | None

    business_id: str | int | None
    business_type: str | None

    result: str
    message: str | None

    before: dict[str, Any]
    after: dict[str, Any]
    metadata: dict[str, Any]

    trace_id: str | None
    request_id: str | None
    source: str | None

    created_at: datetime | None


@dataclass
class AuditRecord:
    """
    默认审计记录对象。

    这是一个轻量数据结构。
    真正项目里可以用 Django Model / SQLAlchemy Model 替换。
    """

    id: str | int

    actor_id: str | int | None
    action: str

    resource_type: str
    resource_id: str | int | None = None

    business_id: str | int | None = None
    business_type: str | None = None

    result: str = "success"
    message: str | None = None

    before: dict[str, Any] = field(default_factory=dict)
    after: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    trace_id: str | None = None
    request_id: str | None = None
    source: str | None = None

    created_at: datetime | None = None


class AuditProviderProtocol(Protocol):
    """
    AuditProvider 协议。

    AuditEngine 不直接操作数据库，只依赖这个协议。

    具体实现可以是：
        - MemoryAuditProvider
        - DjangoAuditProvider
        - SQLAlchemyAuditProvider
        - FileAuditProvider
        - CustomAuditProvider
    """

    name: str
    capability: str

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
        """
        记录一次审计日志。
        """
        ...

    def list_by_resource(
        self,
        *,
        resource_type: str,
        resource_id: str | int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[AuditRecordProtocol]:
        """
        查询某个资源的审计日志。
        """
        ...

    def list_by_actor(
        self,
        *,
        actor_id: str | int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[AuditRecordProtocol]:
        """
        查询某个操作者的审计日志。
        """
        ...
