from __future__ import annotations

from typing import Any

from django.db import models

from packages.metora.core.resources import Resource
from packages.metora.providers.file.protocol import FileProviderProtocol


class FileObject(models.Model, FileProviderProtocol):
    """
    Django 版 FileObject。

    它不需要继承 FileObjectProtocol。
    只要字段和 to_resource() 方法满足 FileObjectProtocol，
    类型上就可以被视为 FileObjectProtocol。
    """
    id = models.AutoField(
        primary_key=True,
    )

    file_name = models.CharField(
        max_length=255,
        db_index=True,
    )

    file_key = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
    )

    content_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    size = models.BigIntegerField(
        null=True,
        blank=True,
    )

    storage = models.CharField(
        max_length=50,
        default="default",
        db_index=True,
    )

    status = models.CharField(
        max_length=50,
        default="pending",
        db_index=True,
    )

    created_by_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    metadata: dict[str, Any] = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "metora_file_object"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["storage"]),
            models.Index(fields=["created_by_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.file_name} ({self.status})"

    def to_resource(self) -> Resource:
        return Resource(
            id=str(self.id),
            type="file",
            title=str(self.file_name),
            status=str(self.status),
            owner_id=str(self.created_by_id),
            created_by=str(self.created_by_id),
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata,
        )