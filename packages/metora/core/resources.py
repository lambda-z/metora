
# metora/core/resources.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ResourceRef:
    """
    ResourceRef 只表示一个资源引用。
    适合放在 ResourceCommand 中。
    """
    type: str
    id: str | int


@dataclass
class Resource:
    """
    Resource 是 Metora 的统一资源视图。

    它不是数据库模型，而是框架内部统一理解资源的方式。
    """
    id: str | int
    type: str

    title: str | None = None
    status: str | None = None

    business_id: str | int | None = None
    business_type: str | None = None

    owner_id: str | int | None = None
    department_id: str | int | None = None

    created_by: str | int | None = None
    updated_by: str | int | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResourceType:
    """
    可选：用于统一声明资源类型。
    """
    code: str
    name: str
    description: str | None = None
