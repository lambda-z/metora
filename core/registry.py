from __future__ import annotations

from typing import Any, Type

from usecases.base import BaseUseCase


class MetoraRegistry:
    def __init__(self):
        self.engines: dict[str, Any] = {}
        self.usecases: dict[str, Any] = {}
        self.providers: dict[tuple[str, str], Any] = {}
        self.hooks: dict[tuple[str, str], list[Any]] = {}

    def register_engine(self, name: str, engine: Any) -> None:
        self.engines[name] = engine

    def get_engine(self, name: str) -> Any:
        if name not in self.engines:
            raise KeyError(f"Engine not registered: {name}")
        return self.engines[name]

    def register_usecase_class(self, action: str, usecase: Type[BaseUseCase]) -> None:
        self.usecases[action] = usecase

    def get_usecase_class(self, action: str) -> Any | None:
        return self.usecases.get(action)

    def register_provider(self, capability: str, name: str, provider: Any) -> None:
        self.providers[(capability, name)] = provider

    def get_provider(self, capability: str, name: str) -> Any:
        key = (capability, name)

        if key not in self.providers:
            raise KeyError(f"Provider not registered: {capability}.{name}")

        return self.providers[key]

    def register_hook(self, business_type: str, hook_name: str, handler: Any) -> None:
        key = (business_type, hook_name)
        self.hooks.setdefault(key, []).append(handler)

    def get_hooks(self, business_type: str, hook_name: str) -> list[Any]:
        return self.hooks.get((business_type, hook_name), [])

    def include(self, module):
        """
        安装一个业务模块。
        只要这个模块有 register(registry) 方法即可。
        """
        module.register(self)
        return self
