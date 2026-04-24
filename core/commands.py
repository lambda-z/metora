# metora/core/commands.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.context import RequestContext
from core.resources import ResourceRef


@dataclass
class ResourceCommand:
    action: str
    resource: ResourceRef
    context: RequestContext
    data: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
