from __future__ import annotations

from packages.metora.core.context import RequestContext
from packages.metora.core.resources import Resource
from packages.metora.providers.audit.memory import MemoryAuditProvider
from packages.metora.providers.audit import AuditRecord


def test_record_should_create_audit_record():
    provider = MemoryAuditProvider()

    context = RequestContext(
        actor_id=1,
        business_id=10001,
        business_type="pre_expense_apply",
        trace_id="trace-001",
        request_id="request-001",
        source="pytest",
    )

    resource = Resource(
        id=10001,
        type="business",
        title="张三的事前支出申请",
        status="submitted",
        business_id=10001,
        business_type="pre_expense_apply",
        owner_id=1,
    )

    record = provider.record(
        context=context,
        action="business.submit",
        resource=resource,
        result="success",
        message="提交业务事项成功",
        before={
            "status": "draft",
        },
        after={
            "status": "submitted",
        },
        metadata={
            "amount": 3000,
        },
    )

    assert isinstance(record, AuditRecord)
    assert record.id
    assert record.actor_id == 1
    assert record.action == "business.submit"
    assert record.resource_type == "business"
    assert record.resource_id == 10001
    assert record.business_id == 10001
    assert record.business_type == "pre_expense_apply"
    assert record.result == "success"
    assert record.message == "提交业务事项成功"
    assert record.before == {"status": "draft"}
    assert record.after == {"status": "submitted"}
    assert record.metadata == {"amount": 3000}
    assert record.trace_id == "trace-001"
    assert record.request_id == "request-001"
    assert record.source == "pytest"
    assert record.created_at is not None

    assert len(provider.records) == 1
    assert provider.records[0].id == record.id


def test_record_should_use_resource_business_when_context_missing_business_info():
    provider = MemoryAuditProvider()

    context = RequestContext(
        actor_id=1,
    )

    resource = Resource(
        id=20001,
        type="business",
        title="合同审批",
        status="draft",
        business_id=20001,
        business_type="contract_review",
        owner_id=1,
    )

    record = provider.record(
        context=context,
        action="business.create",
        resource=resource,
    )

    assert record.business_id == 20001
    assert record.business_type == "contract_review"


def test_record_should_prefer_context_business_info_over_resource_business_info():
    provider = MemoryAuditProvider()

    context = RequestContext(
        actor_id=1,
        business_id=30001,
        business_type="context_business_type",
    )

    resource = Resource(
        id=20001,
        type="business",
        title="合同审批",
        status="draft",
        business_id=20001,
        business_type="resource_business_type",
    )

    record = provider.record(
        context=context,
        action="business.create",
        resource=resource,
    )

    assert record.business_id == 30001
    assert record.business_type == "context_business_type"


def test_record_should_use_default_values():
    provider = MemoryAuditProvider()

    context = RequestContext(
        actor_id=1,
    )

    resource = Resource(
        id=90001,
        type="file",
        title="合同附件.pdf",
        status="uploaded",
    )

    record = provider.record(
        context=context,
        action="file.download",
        resource=resource,
    )

    assert record.result == "success"
    assert record.message is None
    assert record.before == {}
    assert record.after == {}
    assert record.metadata == {}
    assert record.business_id is None
    assert record.business_type is None


def test_list_by_resource_should_return_matching_records_ordered_by_created_at_desc():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource_1 = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    resource_2 = Resource(
        id=20001,
        type="business",
        title="事项 B",
    )

    first = provider.record(
        context=context,
        action="business.create",
        resource=resource_1,
        message="first",
    )

    second = provider.record(
        context=context,
        action="business.submit",
        resource=resource_1,
        message="second",
    )

    provider.record(
        context=context,
        action="business.create",
        resource=resource_2,
        message="other",
    )

    records = provider.list_by_resource(
        resource_type="business",
        resource_id=10001,
    )

    assert len(records) == 2
    assert records[0].id == second.id
    assert records[1].id == first.id


def test_list_by_resource_should_support_string_and_int_resource_id():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    record = provider.record(
        context=context,
        action="business.create",
        resource=resource,
    )

    records = provider.list_by_resource(
        resource_type="business",
        resource_id="10001",
    )

    assert len(records) == 1
    assert records[0].id == record.id


def test_list_by_resource_should_apply_limit_and_offset():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    created_records = []

    for index in range(5):
        record = provider.record(
            context=context,
            action=f"business.action_{index}",
            resource=resource,
            message=f"record-{index}",
        )
        created_records.append(record)

    records = provider.list_by_resource(
        resource_type="business",
        resource_id=10001,
        limit=2,
        offset=1,
    )

    expected_order = list(reversed(created_records))

    assert len(records) == 2
    assert records[0].id == expected_order[1].id
    assert records[1].id == expected_order[2].id


def test_list_by_actor_should_return_matching_records_ordered_by_created_at_desc():
    provider = MemoryAuditProvider()

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    context_1 = RequestContext(actor_id=1)
    context_2 = RequestContext(actor_id=2)

    first = provider.record(
        context=context_1,
        action="business.create",
        resource=resource,
        message="first",
    )

    second = provider.record(
        context=context_1,
        action="business.submit",
        resource=resource,
        message="second",
    )

    provider.record(
        context=context_2,
        action="business.view",
        resource=resource,
        message="other actor",
    )

    records = provider.list_by_actor(
        actor_id=1,
    )

    assert len(records) == 2
    assert records[0].id == second.id
    assert records[1].id == first.id


def test_list_by_actor_should_support_string_and_int_actor_id():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    record = provider.record(
        context=context,
        action="business.create",
        resource=resource,
    )

    records = provider.list_by_actor(
        actor_id="1",
    )

    assert len(records) == 1
    assert records[0].id == record.id


def test_list_by_actor_should_apply_limit_and_offset():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    created_records = []

    for index in range(5):
        record = provider.record(
            context=context,
            action=f"business.action_{index}",
            resource=resource,
            message=f"record-{index}",
        )
        created_records.append(record)

    records = provider.list_by_actor(
        actor_id=1,
        limit=2,
        offset=1,
    )

    expected_order = list(reversed(created_records))

    assert len(records) == 2
    assert records[0].id == expected_order[1].id
    assert records[1].id == expected_order[2].id


def test_list_by_resource_should_return_empty_when_no_match():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    provider.record(
        context=context,
        action="business.create",
        resource=resource,
    )

    records = provider.list_by_resource(
        resource_type="business",
        resource_id=99999,
    )

    assert records == []


def test_list_by_actor_should_return_empty_when_no_match():
    provider = MemoryAuditProvider()

    context = RequestContext(actor_id=1)

    resource = Resource(
        id=10001,
        type="business",
        title="事项 A",
    )

    provider.record(
        context=context,
        action="business.create",
        resource=resource,
    )

    records = provider.list_by_actor(
        actor_id=99999,
    )

    assert records == []
