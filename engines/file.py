from __future__ import annotations

from typing import Any

from core.context import RequestContext
from core.resources import Resource
from engines.base import BaseEngine
from providers.file.protocol import FileObjectProtocol, FileProviderProtocol
from providers.storage.protocol import StorageProviderProtocol


class FileEngine(BaseEngine):
    """
    FileEngine：文件引擎。

    核心职责：
        1. 初始化上传
        2. 确认上传完成
        3. 查询文件
        4. 生成下载地址
        5. 删除文件
        6. 绑定文件到业务资源
        7. 查询某个资源下的文件
        8. 将文件解析为 Resource

    不负责：
        - 权限判断
        - 审计记录
        - 业务表单逻辑
        - 具体对象存储 SDK 调用
    """

    engine_name = "file"

    def __init__(
        self,
        file_provider: FileProviderProtocol | None = None,
        storage_provider: StorageProviderProtocol | None = None,
        file_provider_name: str = "default",
        storage_provider_name: str = "default",
        registry=None,
    ):
        super().__init__(registry=registry)
        self.file_provider = file_provider
        self.storage_provider = storage_provider
        self.file_provider_name = file_provider_name
        self.storage_provider_name = storage_provider_name

    def get_file_provider(self) -> FileProviderProtocol:
        if self.file_provider:
            return self.file_provider

        if not self.registry:
            raise RuntimeError("FileEngine requires file_provider or registry")

        return self.registry.get_provider(
            capability="file",
            name=self.file_provider_name,
        )

    def get_storage_provider(self) -> StorageProviderProtocol:
        if self.storage_provider:
            return self.storage_provider

        if not self.registry:
            raise RuntimeError("FileEngine requires storage_provider or registry")

        return self.registry.get_provider(
            capability="storage",
            name=self.storage_provider_name,
        )

    def init_upload(
        self,
        *,
        context: RequestContext,
        file_name: str,
        content_type: str | None = None,
        size: int | None = None,
        folder: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        初始化上传。

        典型流程：
            1. StorageProvider 生成 file_key
            2. FileProvider 创建 file_object，状态为 pending
            3. StorageProvider 生成 upload_url
            4. 返回给前端
        """

        file_provider = self.get_file_provider()
        storage_provider = self.get_storage_provider()

        file_key = storage_provider.build_file_key(
            file_name=file_name,
            folder=folder,
        )

        file_object = file_provider.create_file(
            file_name=file_name,
            file_key=file_key,
            content_type=content_type,
            size=size,
            storage=storage_provider.name,
            status="pending",
            created_by_id=context.actor_id,
            metadata=metadata or {},
        )

        upload_info = storage_provider.init_upload(
            file_key=file_key,
            content_type=content_type,
        )

        return {
            "fileId": file_object.id,
            "fileName": file_object.file_name,
            "fileKey": file_object.file_key,
            "status": file_object.status,
            "upload": upload_info,
        }

    def confirm_upload(
        self,
        *,
        file_id: str | int,
        size: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FileObjectProtocol:
        """
        确认上传完成。

        前端上传到对象存储成功后，调用这个方法把文件状态改为 uploaded。
        """

        return self.get_file_provider().update_file_status(
            file_id=file_id,
            status="uploaded",
            size=size,
            metadata=metadata or {},
        )

    def get_file(
        self,
        file_id: str | int,
    ) -> FileObjectProtocol:
        """
        获取文件元数据。
        """

        return self.get_file_provider().get_file(file_id)

    def get_download_url(
        self,
        *,
        file_id: str | int,
        expires: int = 300,
    ) -> str:
        """
        获取文件下载地址。

        注意：
            权限判断不要放在这里。
            应该由 UseCase 先调用 PermissionEngine.assert_can()。
        """

        file_object = self.get_file_provider().get_file(file_id)

        return self.get_storage_provider().get_download_url(
            file_key=file_object.file_key,
            expires=expires,
        )

    def delete_file(
        self,
        *,
        file_id: str | int,
    ) -> None:
        """
        删除文件。

        通常包括：
            1. 删除真实存储文件
            2. 删除或标记删除文件元数据
        """

        file_provider = self.get_file_provider()
        storage_provider = self.get_storage_provider()

        file_object = file_provider.get_file(file_id)

        storage_provider.delete(file_key=file_object.file_key)

        file_provider.delete_file(file_id=file_id)

    def bind_file(
        self,
        *,
        context: RequestContext,
        file_id: str | int,
        resource_type: str,
        resource_id: str | int,
        usage: str | None = None,
    ):
        """
        将文件绑定到某个资源。

        例如：
            file -> business
            file -> form
            file -> document
            file -> task
        """

        return self.get_file_provider().bind_file(
            file_id=file_id,
            resource_type=resource_type,
            resource_id=resource_id,
            usage=usage,
            created_by_id=context.actor_id,
        )

    def list_files_by_resource(
        self,
        *,
        resource_type: str,
        resource_id: str | int,
        usage: str | None = None,
    ) -> list[FileObjectProtocol]:
        """
        查询某个资源下绑定的文件。
        """

        return self.get_file_provider().list_files_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
            usage=usage,
        )

    def resolve_resource(
        self,
        resource_id: str | int,
    ) -> Resource:
        """
        将 file_id 解析成 Metora Resource。
        """

        file_object = self.get_file_provider().get_file(resource_id)
        return file_object.to_resource()

    def get_available_actions(
        self,
        *,
        context: RequestContext,
        resource: Resource,
    ) -> list[str]:
        """
        返回文件资源的候选动作。

        最终是否可用还需要 PermissionEngine 过滤。
        """

        if resource.status == "uploaded":
            return [
                "file.view",
                "file.download",
                "file.delete",
                "file.bind",
            ]

        if resource.status == "pending":
            return [
                "file.confirm_upload",
                "file.delete",
            ]

        return [
            "file.view",
        ]
