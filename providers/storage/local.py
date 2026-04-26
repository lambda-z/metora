from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from providers.storage.protocol import StorageProviderProtocol


class LocalStorageProvider(StorageProviderProtocol):
    """
    本地磁盘 StorageProvider。

    负责真实文件存储：
        - 生成 file_key
        - 返回上传路径
        - 返回下载路径
        - 删除真实文件
    """

    name = "local"
    capability = "storage"

    def __init__(self, root_dir: str | Path = "./runtime/uploads"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def build_file_key(
        self,
        *,
        file_name: str,
        folder: str | None = None,
    ) -> str:
        suffix = Path(file_name).suffix
        safe_name = f"{uuid4()}{suffix}"

        if folder:
            return f"{folder.strip('/')}/{safe_name}"

        return safe_name

    def init_upload(
        self,
        *,
        file_key: str,
        content_type: str | None = None,
        expires: int = 300,
    ) -> dict:
        """
        本地磁盘没有预签名 URL。

        这里返回一个 local_path，
        Web 层可以用这个路径保存上传文件。
        """

        path = self._resolve_path(file_key)
        path.parent.mkdir(parents=True, exist_ok=True)

        return {
            "method": "LOCAL_FILE_WRITE",
            "file_key": file_key,
            "local_path": str(path),
            "content_type": content_type,
            "expires": expires,
        }

    def save_file(
        self,
        *,
        file_key: str,
        source_path: str | Path,
    ) -> None:
        """
        从本地临时路径复制文件到存储目录。

        这个方法不是协议必须项，但本地开发很有用。
        """

        target_path = self._resolve_path(file_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(source_path, target_path)

    def get_download_url(
        self,
        *,
        file_key: str,
        expires: int = 300,
    ) -> str:
        """
        本地版本先返回文件路径。

        如果接入 FastAPI / Django，可以在 Web 层将它转换成静态文件 URL。
        """

        path = self._resolve_path(file_key)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_key}")

        return str(path)

    def delete(
        self,
        *,
        file_key: str,
    ) -> None:
        path = self._resolve_path(file_key)

        if path.exists():
            path.unlink()

    def _resolve_path(self, file_key: str) -> Path:
        path = self.root_dir / file_key

        resolved_root = self.root_dir.resolve()
        resolved_path = path.resolve()

        if not str(resolved_path).startswith(str(resolved_root)):
            raise ValueError("Invalid file_key: path traversal detected")

        return resolved_path
