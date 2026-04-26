from __future__ import annotations

from typing import Protocol


class StorageProviderProtocol(Protocol):
    """
    StorageProvider 负责真实文件存储。

    例如：
        本地磁盘
        OSS
        MinIO
        S3
    """

    name: str
    capability: str

    def build_file_key(
        self,
        *,
        file_name: str,
        folder: str | None = None,
    ) -> str:
        ...

    def init_upload(
        self,
        *,
        file_key: str,
        content_type: str | None = None,
        expires: int = 300,
    ) -> dict:
        """
        初始化上传。

        可以返回：
            - upload_url
            - method
            - headers
            - file_key
        """
        ...

    def get_download_url(
        self,
        *,
        file_key: str,
        expires: int = 300,
    ) -> str:
        ...

    def delete(
        self,
        *,
        file_key: str,
    ) -> None:
        ...
