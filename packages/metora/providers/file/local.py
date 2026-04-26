from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from packages.metora.core.resources import Resource
from packages.metora.providers.file.protocol import (
    FileBindingProtocol,
    FileObjectProtocol,
    FileProviderProtocol,
)


@dataclass
class LocalFileObject:
    id: str
    file_name: str
    file_key: str
    content_type: str | None = None
    size: int | None = None
    storage: str = "local"
    status: str = "pending"

    created_by_id: str | int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_resource(self) -> Resource:
        return Resource(
            id=self.id,
            type="file",
            title=self.file_name,
            status=self.status,
            owner_id=self.created_by_id,
            created_by=self.created_by_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata={
                "fileKey": self.file_key,
                "contentType": self.content_type,
                "size": self.size,
                "storage": self.storage,
                **self.metadata,
            },
        )


@dataclass
class LocalFileBinding:
    id: str
    file_id: str | int

    resource_type: str
    resource_id: str | int

    usage: str | None = None
    created_by_id: str | int | None = None
    created_at: datetime | None = None


class LocalFileProvider(FileProviderProtocol):
    """
    本地文件元数据 Provider。

    它负责保存：
        - file_object 元数据
        - file_binding 绑定关系

    注意：
        它不负责真实文件存储。
        真实文件读写应该交给 LocalStorageProvider。
    """

    name = "local"
    capability = "file"

    def __init__(self, metadata_path: str | Path = "./runtime/file_metadata.json"):
        self.metadata_path = Path(metadata_path)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

        self.files: dict[str, LocalFileObject] = {}
        self.bindings: dict[str, LocalFileBinding] = {}

        self._load()

    def create_file(
        self,
        *,
        file_name: str,
        file_key: str,
        content_type: str | None = None,
        size: int | None = None,
        storage: str = "local",
        status: str = "pending",
        created_by_id: str | int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FileObjectProtocol:
        now = datetime.now()
        file_id = str(uuid4())

        file_object = LocalFileObject(
            id=file_id,
            file_name=file_name,
            file_key=file_key,
            content_type=content_type,
            size=size,
            storage=storage,
            status=status,
            created_by_id=created_by_id,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self.files[file_id] = file_object
        self._save()

        return file_object

    def get_file(self, file_id: str | int) -> FileObjectProtocol:
        file_id = str(file_id)

        if file_id not in self.files:
            raise KeyError(f"File not found: {file_id}")

        return self.files[file_id]

    def update_file_status(
        self,
        *,
        file_id: str | int,
        status: str,
        size: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FileObjectProtocol:
        file_object = self.get_file(file_id)

        file_object.status = status
        file_object.updated_at = datetime.now()

        if size is not None:
            file_object.size = size

        if metadata:
            file_object.metadata.update(metadata)

        self._save()

        return file_object

    def delete_file(
        self,
        *,
        file_id: str | int,
    ) -> None:
        file_id = str(file_id)

        if file_id not in self.files:
            raise KeyError(f"File not found: {file_id}")

        del self.files[file_id]

        binding_ids = [
            binding_id
            for binding_id, binding in self.bindings.items()
            if str(binding.file_id) == file_id
        ]

        for binding_id in binding_ids:
            del self.bindings[binding_id]

        self._save()

    def bind_file(
        self,
        *,
        file_id: str | int,
        resource_type: str,
        resource_id: str | int,
        usage: str | None = None,
        created_by_id: str | int | None = None,
    ) -> FileBindingProtocol:
        self.get_file(file_id)

        binding_id = str(uuid4())

        binding = LocalFileBinding(
            id=binding_id,
            file_id=file_id,
            resource_type=resource_type,
            resource_id=resource_id,
            usage=usage,
            created_by_id=created_by_id,
            created_at=datetime.now(),
        )

        self.bindings[binding_id] = binding
        self._save()

        return binding

    def list_files_by_resource(
        self,
        *,
        resource_type: str,
        resource_id: str | int,
        usage: str | None = None,
    ) -> list[FileObjectProtocol]:
        matched_bindings = [
            binding
            for binding in self.bindings.values()
            if binding.resource_type == resource_type
            and str(binding.resource_id) == str(resource_id)
            and (usage is None or binding.usage == usage)
        ]

        result: list[FileObjectProtocol] = []

        for binding in matched_bindings:
            file_id = str(binding.file_id)

            if file_id in self.files:
                result.append(self.files[file_id])

        return result

    def _load(self) -> None:
        if not self.metadata_path.exists():
            return

        raw = json.loads(self.metadata_path.read_text(encoding="utf-8"))

        self.files = {
            item["id"]: LocalFileObject(
                **{
                    **item,
                    "created_at": self._parse_datetime(item.get("created_at")),
                    "updated_at": self._parse_datetime(item.get("updated_at")),
                }
            )
            for item in raw.get("files", [])
        }

        self.bindings = {
            item["id"]: LocalFileBinding(
                **{
                    **item,
                    "created_at": self._parse_datetime(item.get("created_at")),
                }
            )
            for item in raw.get("bindings", [])
        }

    def _save(self) -> None:
        data = {
            "files": [
                self._serialize_dataclass(file)
                for file in self.files.values()
            ],
            "bindings": [
                self._serialize_dataclass(binding)
                for binding in self.bindings.values()
            ],
        }

        self.metadata_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _serialize_dataclass(self, obj) -> dict[str, Any]:
        data = asdict(obj)

        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        return data

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None

        return datetime.fromisoformat(value)
