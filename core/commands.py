# metora/core/commands.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.resources import ResourceRef


@dataclass
class RequestContext:
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


@dataclass
class ResourceCommand:
    action: str
    resource: ResourceRef
    context: RequestContext
    data: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
