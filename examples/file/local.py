# =========================================================
# demo
# =========================================================
import json
from pathlib import Path

from core.context import MetoraContext, RequestContext
from core.registry import MetoraRegistry
from core.resources import ResourceRef
from engines.file import FileEngine
from providers.file.local import LocalFileProvider
from providers.storage.local import LocalStorageProvider


def main():
    print("========== Metora FileEngine Local Demo ==========")

    runtime_dir = Path("./runtime")
    runtime_dir.mkdir(parents=True, exist_ok=True)

    sample_source = runtime_dir / "sample.txt"
    sample_source.write_text(
        "Hello Metora FileEngine.\n这是一个本地文件上传示例。",
        encoding="utf-8",
    )

    registry = MetoraRegistry()

    local_file_provider = LocalFileProvider(
        metadata_path="./runtime/file_metadata.json",
    )

    local_storage_provider = LocalStorageProvider(
        root_dir="./runtime/uploads",
    )

    registry.register_provider(
        capability="file",
        name="default",
        provider=local_file_provider,
    )

    registry.register_provider(
        capability="storage",
        name="default",
        provider=local_storage_provider,
    )

    file_engine = FileEngine(
        file_provider_name="default",
        storage_provider_name="default",
        registry=registry,
    )

    registry.register_engine(
        "file",
        file_engine,
    )

    metora = MetoraContext(registry)

    context = RequestContext(
        actor_id=1,
        source="demo",
    )

    print("\n1. 初始化上传")
    upload_result = metora.engine.file.init_upload(
        context=context,
        file_name="sample.txt",
        content_type="text/plain",
        folder="business/10001",
        metadata={
            "scene": "demo",
        },
    )

    print(json.dumps(upload_result, ensure_ascii=False, indent=2))

    file_id = upload_result["fileId"]
    file_key = upload_result["fileKey"]

    print("\n2. 模拟把文件写入本地存储")
    local_storage_provider.save_file(
        file_key=file_key,
        source_path=sample_source,
    )

    saved_path = Path(upload_result["upload"]["local_path"])
    file_size = saved_path.stat().st_size

    print(f"文件已保存到: {saved_path}")

    print("\n3. 确认上传完成")
    file_object = metora.engine.file.confirm_upload(
        file_id=file_id,
        size=file_size,
        metadata={
            "confirmed": True,
        },
    )

    print(file_object)

    print("\n4. 绑定文件到业务资源 business:10001")
    binding = metora.engine.file.bind_file(
        context=context,
        file_id=file_id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    print(binding)

    print("\n5. 查询 business:10001 下的附件")
    files = metora.engine.file.list_files_by_resource(
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    for item in files:
        print(item)

    print("\n6. 获取下载地址")
    download_url = metora.engine.file.get_download_url(
        file_id=file_id,
    )

    print(download_url)

    print("\n7. 解析 Resource")
    resource = metora.resource.resolve(
        ResourceRef(
            type="file",
            id=file_id,
        )
    )

    print(resource)

    print("\n8. 获取可用动作")
    actions = metora.engine.file.get_available_actions(
        context=context,
        resource=resource,
    )

    print(actions)

    print("\n========== Demo Finished ==========")


if __name__ == "__main__":
    main()