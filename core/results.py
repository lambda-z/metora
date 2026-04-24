from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionResult:
    ok: bool
    code: str
    message: str

    action: str | None = None
    resource: dict[str, Any] | None = None
    result: dict[str, Any] = field(default_factory=dict)
    effects: dict[str, bool] = field(default_factory=dict)
    refresh: dict[str, bool] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    http_status: int = 200

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "resource": self.resource,
            "result": self.result,
            "effects": self.effects,
            "refresh": self.refresh,
            "events": self.events,
        }
