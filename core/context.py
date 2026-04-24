# metora/core/context.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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


class AdapterAccessor:
    """
    Adapter 快捷访问器。

    允许：
        self.context.adapter.get("notification", "wechat")
        self.context.adapter.get("storage", "oss")
    """

    def __init__(self, registry):
        self.registry = registry

    def get(self, capability: str, name: str):
        return self.registry.get_adapter(capability, name)


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


class MetoraContext:
    """
    Metora 运行时上下文。

    它是 UseCase / Engine 访问框架资源的入口，
    主要包装 registry，提供更语义化的快捷访问方式。
    """

    def __init__(self, registry):
        self.registry = registry
        self.engine = EngineAccessor(registry)
        self.adapter = AdapterAccessor(registry)
        self.persistence = PersistenceAccessor(registry)

    def get_engine(self, name: str):
        return self.registry.get_engine(name)

    def get_adapter(self, capability: str, name: str):
        return self.registry.get_adapter(capability, name)

    def get_persistence(self, name: str):
        return self.registry.get_persistence(name)
