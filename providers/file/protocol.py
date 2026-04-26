from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from core.resources import Resource


@runtime_checkable
class FileObjectProtocol(Protocol):
    id: str | int
    file_name: str
    file_key: str
    content_type: str | None
    size: int | None
    storage: str
    status: str

    created_by_id: str | int | None
    created_at: datetime | None
    updated_at: datetime | None

    metadata: dict[str, Any]

    def to_resource(self) -> Resource:
        ...


@runtime_checkable
class FileBindingProtocol(Protocol):
    id: str | int
    file_id: str | int

    resource_type: str
    resource_id: str | int

    usage: str | None
    created_by_id: str | int | None
    created_at: datetime | None


class FileProviderProtocol(Protocol):
    """
    FileProvider 负责文件元数据持久化。

    它不负责真实文件存储。
    真实文件上传、下载 URL 由 StorageProvider 负责。
    """

    name: str
    capability: str

    def create_file(
        self,
        *,
        file_name: str,
        file_key: str,
        content_type: str | None = None,
        size: int | None = None,
        storage: str = "default",
        status: str = "pending",
        created_by_id: str | int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FileObjectProtocol:
        ...

    def get_file(self, file_id: str | int) -> FileObjectProtocol:
        ...

    def update_file_status(
        self,
        *,
        file_id: str | int,
        status: str,
        size: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FileObjectProtocol:
        ...

    def delete_file(
        self,
        *,
        file_id: str | int,
    ) -> None:
        ...

    def bind_file(
        self,
        *,
        file_id: str | int,
        resource_type: str,
        resource_id: str | int,
        usage: str | None = None,
        created_by_id: str | int | None = None,
    ) -> FileBindingProtocol:
        ...

    def list_files_by_resource(
        self,
        *,
        resource_type: str,
        resource_id: str | int,
        usage: str | None = None,
    ) -> list[FileObjectProtocol]:
        ...
