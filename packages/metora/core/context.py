# metora/core/context.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from packages.metora.core.resources import ResourceRef


@dataclass
class RequestContext:
    """
    一次业务请求的上下文。

    它描述：
    谁在操作、在哪个业务中操作、当前任务是什么、请求来源是什么。
    """

    actor_id: str | int | None = None

    business_id: str | int | None = None
    business_type: str | None = None

    task_id: str | int | None = None
    workflow_id: str | int | None = None
    node_id: str | None = None

    request_id: str | None = None
    trace_id: str | None = None
    source: str | None = None

    extra: dict[str, Any] = field(default_factory=dict)


class EngineAccessor:
    """
    Engine 快捷访问器。

    允许在 UseCase 中使用：
        self.context.engine.business
        self.context.engine.workflow
        self.context.engine.form
        self.context.engine.permission
    """

    def __init__(self, registry):
        self.registry = registry

    def __getattr__(self, name: str):
        return self.registry.get_engine(name)


class ProviderAccessor:
    """
    Provider 快捷访问器。

    允许：
        self.context.provider.get("notification", "wechat")
        self.context.provider.get("storage", "oss")
    """

    def __init__(self, registry):
        self.registry = registry

    def get(self, capability: str, name: str):
        return self.registry.get_provider(capability, name)


class PersistenceAccessor:
    """
    PersistenceProvider 快捷访问器。

    允许：
        self.context.persistence.business
        self.context.persistence.notification
    """

    def __init__(self, registry):
        self.registry = registry

    def __getattr__(self, name: str):
        return self.registry.get_persistence(name)


class ResourceAccessor:
    """
    Resource 解析访问器。

    用于把 ResourceRef 转换成运行时 Resource。
    """

    def __init__(self, registry):
        self.registry = registry

    def resolve(self, resource_ref: ResourceRef):
        """
        根据 resource_ref 解析 Resource。

        resource_ref:
            ResourceRef(type="business", id=10001)
            ResourceRef(type="task", id=50001)
            ResourceRef(type="form", id=30001)
        """

        engine = self.registry.get_engine(resource_ref.type)

        if not hasattr(engine, "resolve_resource"):
            raise RuntimeError(
                f"Engine '{resource_ref.type}' does not support resolve_resource()"
            )

        return engine.resolve_resource(resource_ref.id)


class MetoraContext:
    """
    Metora 运行时上下文。

    它是 UseCase / Engine 访问框架资源的入口，
    主要包装 registry，提供更语义化的快捷访问方式。
    """

    def __init__(self, registry):
        self.registry = registry
        self.engine = EngineAccessor(registry)
        self.provider = ProviderAccessor(registry)
        self.persistence = PersistenceAccessor(registry)
        self.resource = ResourceAccessor(registry)

    def get_engine(self, name: str):
        return self.registry.get_engine(name)

    def get_provider(self, capability: str, name: str):
        return self.registry.get_provider(capability, name)

    def get_persistence(self, name: str):
        return self.registry.get_persistence(name)
