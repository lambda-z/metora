from __future__ import annotations

from typing import Any

from packages.metora.core.context import RequestContext
from packages.metora.core.resources import Resource
from packages.metora.engines.base import BaseEngine
from packages.metora.providers.audit.protocol import (
    AuditProviderProtocol,
    AuditRecordProtocol,
)


class AuditEngine(BaseEngine):
    """
    AuditEngine：审计引擎。

    它只做一件事：

        对外提供统一的审计记录入口。

    具体审计日志怎么存，交给 AuditProvider。

    它适合记录：
        - 谁创建了业务事项
        - 谁提交了申请
        - 谁审批了任务
        - 谁驳回了流程
        - 谁下载了文件
        - 谁查看了敏感字段
        - 谁修改了配置
    """

    engine_name = "audit"

    def __init__(
        self,
        provider: AuditProviderProtocol | None = None,
        provider_name: str = "default",
        registry=None,
    ):
        super().__init__(registry=registry)
        self.provider = provider
        self.provider_name = provider_name

    def get_provider(self) -> AuditProviderProtocol:
        """
        获取 AuditProvider。

        优先使用构造函数传入的 provider。
        如果没有，则从 registry 中获取。
        """

        if self.provider:
            return self.provider

        if not self.registry:
            raise RuntimeError("AuditEngine requires provider or registry")

        return self.registry.get_provider(
            capability="audit",
            name=self.provider_name,
        )

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
        记录审计日志。

        UseCase 中推荐这样调用：

            self.engine.audit.record(
                context=command.context,
                action=command.action,
                resource=resource,
                result="success",
                message="提交业务事项",
            )
        """

        return self.get_provider().record(
            context=context,
            action=action,
            resource=resource,
            result=result,
            message=message,
            before=before or {},
            after=after or {},
            metadata=metadata or {},
        )

    def record_success(
        self,
        *,
        context: RequestContext,
        action: str,
        resource: Resource,
        message: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditRecordProtocol:
        """
        记录成功操作。
        """

        return self.record(
            context=context,
            action=action,
            resource=resource,
            result="success",
            message=message,
            before=before,
            after=after,
            metadata=metadata,
        )

    def record_failure(
        self,
        *,
        context: RequestContext,
        action: str,
        resource: Resource,
        message: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditRecordProtocol:
        """
        记录失败操作。
        """

        return self.record(
            context=context,
            action=action,
            resource=resource,
            result="failure",
            message=message,
            before=before,
            after=after,
            metadata=metadata,
        )

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

        return self.get_provider().list_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit,
            offset=offset,
        )

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

        return self.get_provider().list_by_actor(
            actor_id=actor_id,
            limit=limit,
            offset=offset,
        )
