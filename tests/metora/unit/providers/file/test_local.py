from __future__ import annotations

import json
from pathlib import Path

import pytest

from packages.metora.providers import LocalFileProvider
from packages.metora.core.resources import Resource


@pytest.fixture
def provider(tmp_path: Path) -> LocalFileProvider:
    return LocalFileProvider(
        metadata_path=tmp_path / "file_metadata.json",
    )


def test_create_file_should_create_metadata_file(provider: LocalFileProvider):
    file_object = provider.create_file(
        file_name="test.pdf",
        file_key="business/10001/test.pdf",
        content_type="application/pdf",
        size=1024,
        storage="local",
        status="pending",
        created_by_id=1,
        metadata={
            "scene": "unit_test",
        },
    )

    assert file_object.id
    assert file_object.file_name == "test.pdf"
    assert file_object.file_key == "business/10001/test.pdf"
    assert file_object.content_type == "application/pdf"
    assert file_object.size == 1024
    assert file_object.storage == "local"
    assert file_object.status == "pending"
    assert file_object.created_by_id == 1
    assert file_object.metadata["scene"] == "unit_test"
    assert file_object.created_at is not None
    assert file_object.updated_at is not None

    assert provider.metadata_path.exists()


def test_get_file_should_return_existing_file(provider: LocalFileProvider):
    created = provider.create_file(
        file_name="receipt.png",
        file_key="receipt.png",
    )

    found = provider.get_file(created.id)

    assert found.id == created.id
    assert found.file_name == "receipt.png"
    assert found.file_key == "receipt.png"


def test_get_file_should_raise_key_error_when_not_found(provider: LocalFileProvider):
    with pytest.raises(KeyError):
        provider.get_file("not-exists")


def test_update_file_status_should_update_status_size_and_metadata(provider: LocalFileProvider):
    file_object = provider.create_file(
        file_name="contract.docx",
        file_key="contract.docx",
        metadata={
            "old": True,
        },
    )

    updated = provider.update_file_status(
        file_id=file_object.id,
        status="uploaded",
        size=2048,
        metadata={
            "confirmed": True,
        },
    )

    assert updated.status == "uploaded"
    assert updated.size == 2048
    assert updated.metadata["old"] is True
    assert updated.metadata["confirmed"] is True
    assert updated.updated_at is not None


def test_bind_file_should_create_binding(provider: LocalFileProvider):
    file_object = provider.create_file(
        file_name="attachment.pdf",
        file_key="attachment.pdf",
    )

    binding = provider.bind_file(
        file_id=file_object.id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
        created_by_id=1,
    )

    assert binding.id
    assert binding.file_id == file_object.id
    assert binding.resource_type == "business"
    assert binding.resource_id == 10001
    assert binding.usage == "attachment"
    assert binding.created_by_id == 1
    assert binding.created_at is not None


def test_bind_file_should_raise_when_file_not_found(provider: LocalFileProvider):
    with pytest.raises(KeyError):
        provider.bind_file(
            file_id="not-exists",
            resource_type="business",
            resource_id=10001,
        )


def test_list_files_by_resource_should_return_bound_files(provider: LocalFileProvider):
    file_1 = provider.create_file(
        file_name="a.pdf",
        file_key="a.pdf",
    )
    file_2 = provider.create_file(
        file_name="b.pdf",
        file_key="b.pdf",
    )
    file_3 = provider.create_file(
        file_name="c.pdf",
        file_key="c.pdf",
    )

    provider.bind_file(
        file_id=file_1.id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )
    provider.bind_file(
        file_id=file_2.id,
        resource_type="business",
        resource_id=10001,
        usage="material",
    )
    provider.bind_file(
        file_id=file_3.id,
        resource_type="business",
        resource_id=20001,
        usage="attachment",
    )

    all_files = provider.list_files_by_resource(
        resource_type="business",
        resource_id=10001,
    )

    attachment_files = provider.list_files_by_resource(
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    assert {item.id for item in all_files} == {file_1.id, file_2.id}
    assert len(attachment_files) == 1
    assert attachment_files[0].id == file_1.id


def test_list_files_by_resource_should_support_string_and_int_resource_id(
    provider: LocalFileProvider,
):
    file_object = provider.create_file(
        file_name="a.pdf",
        file_key="a.pdf",
    )

    provider.bind_file(
        file_id=file_object.id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    files = provider.list_files_by_resource(
        resource_type="business",
        resource_id="10001",
        usage="attachment",
    )

    assert len(files) == 1
    assert files[0].id == file_object.id


def test_delete_file_should_remove_file_and_related_bindings(provider: LocalFileProvider):
    file_object = provider.create_file(
        file_name="delete.pdf",
        file_key="delete.pdf",
    )

    provider.bind_file(
        file_id=file_object.id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    assert len(provider.bindings) == 1

    provider.delete_file(
        file_id=file_object.id,
    )

    assert str(file_object.id) not in provider.files
    assert len(provider.bindings) == 0

    with pytest.raises(KeyError):
        provider.get_file(file_object.id)


def test_delete_file_should_raise_when_file_not_found(provider: LocalFileProvider):
    with pytest.raises(KeyError):
        provider.delete_file(
            file_id="not-exists",
        )


def test_to_resource_should_return_file_resource(provider: LocalFileProvider):
    file_object = provider.create_file(
        file_name="resource.txt",
        file_key="resource.txt",
        content_type="text/plain",
        size=100,
        storage="local",
        status="uploaded",
        created_by_id=1,
        metadata={
            "custom": "value",
        },
    )

    resource = file_object.to_resource()

    assert isinstance(resource, Resource)
    assert resource.id == file_object.id
    assert resource.type == "file"
    assert resource.title == "resource.txt"
    assert resource.status == "uploaded"
    assert resource.owner_id == 1
    assert resource.created_by == 1
    assert resource.metadata["fileKey"] == "resource.txt"
    assert resource.metadata["contentType"] == "text/plain"
    assert resource.metadata["size"] == 100
    assert resource.metadata["storage"] == "local"
    assert resource.metadata["custom"] == "value"


def test_provider_should_persist_and_reload_data(tmp_path: Path):
    metadata_path = tmp_path / "file_metadata.json"

    provider_1 = LocalFileProvider(
        metadata_path=metadata_path,
    )

    file_object = provider_1.create_file(
        file_name="persist.pdf",
        file_key="persist.pdf",
        content_type="application/pdf",
        size=100,
        status="uploaded",
        created_by_id=1,
        metadata={
            "persisted": True,
        },
    )

    binding = provider_1.bind_file(
        file_id=file_object.id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
        created_by_id=1,
    )

    provider_2 = LocalFileProvider(
        metadata_path=metadata_path,
    )

    loaded_file = provider_2.get_file(file_object.id)

    assert loaded_file.id == file_object.id
    assert loaded_file.file_name == "persist.pdf"
    assert loaded_file.file_key == "persist.pdf"
    assert loaded_file.content_type == "application/pdf"
    assert loaded_file.size == 100
    assert loaded_file.status == "uploaded"
    assert loaded_file.created_by_id == 1
    assert loaded_file.metadata["persisted"] is True
    assert loaded_file.created_at is not None
    assert loaded_file.updated_at is not None

    assert binding.id in provider_2.bindings

    files = provider_2.list_files_by_resource(
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    assert len(files) == 1
    assert files[0].id == file_object.id


def test_metadata_json_should_have_files_and_bindings(provider: LocalFileProvider):
    file_object = provider.create_file(
        file_name="json.pdf",
        file_key="json.pdf",
    )

    provider.bind_file(
        file_id=file_object.id,
        resource_type="business",
        resource_id=10001,
        usage="attachment",
    )

    raw = json.loads(provider.metadata_path.read_text(encoding="utf-8"))

    assert "files" in raw
    assert "bindings" in raw
    assert len(raw["files"]) == 1
    assert len(raw["bindings"]) == 1
    assert raw["files"][0]["id"] == file_object.id
    assert raw["files"][0]["created_at"] is not None
    assert raw["files"][0]["updated_at"] is not None
