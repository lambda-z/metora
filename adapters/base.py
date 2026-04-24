from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AdapterResult:
    ok: bool
    code: str
    message: str
    raw: dict[str, Any] = field(default_factory=dict)


class AdapterBase(ABC):
    name: str = "base"
    capability: str = "base"

    def validate_config(self) -> None:
        pass

    def health_check(self) -> AdapterResult:
        return AdapterResult(
            ok=True,
            code="OK",
            message="Adapter is healthy",
        )
