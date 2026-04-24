
from __future__ import annotations

from typing import Any


class BaseEngine:
    engine_name = "base"

    def __init__(self, registry=None):
        self.registry = registry

    def initialize(self) -> None:
        pass

    def validate(self, *args, **kwargs) -> Any:
        return None

    def get_state(self, *args, **kwargs) -> Any:
        return None

    def get_available_actions(self, *args, **kwargs) -> list[str]:
        return []
