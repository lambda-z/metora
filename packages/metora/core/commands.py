# metora/core/commands.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from packages.metora.core.context import RequestContext
from packages.metora.core.resources import ResourceRef


@dataclass
class ResourceCommand:
    """
    ResourceCommand 是 Metora 中的一次“资源动作指令”。

    它用于把外部请求统一转换成框架内部可以识别、分发和执行的标准对象。

    可以理解为一句话：

        谁，在什么上下文中，对哪个资源，执行什么动作，携带什么参数。

    例如前端请求：

        {
            "action": "business.submit",
            "resource": {
                "type": "business",
                "id": 10001
            },
            "context": {
                "actorId": 1,
                "businessType": "pre_expense_apply"
            },
            "data": {
                "comment": "提交申请"
            }
        }

    在后端会被转换成：

        ResourceCommand(
            action="business.submit",
            resource_ref=ResourceRef(type="business", id=10001),
            context=RequestContext(actor_id=1, business_type="pre_expense_apply"),
            data={"comment": "提交申请"}
        )

    ResourceCommand 不负责执行业务逻辑。
    它只是“指令对象”。

    真正的执行流程是：

        ResourceCommand
            ↓
        MetoraRuntime
            ↓
        ActionRegistry / UseCaseRegistry
            ↓
        UseCase
            ↓
        Engine / Persistence / Adapter
    """

    action: str
    """
    动作名称。

    表示这次请求要执行什么操作。

    推荐使用“资源类型.动作”的命名方式：

        business.create
        business.submit
        business.withdraw
        business.archive

        task.approve
        task.reject
        task.return

        form.save
        form.validate
        form.freeze

        document.save
        document.finalize
        document.export_pdf

        file.upload
        file.download

        notification.read

    action 的作用：
        1. Runtime 根据 action 找到对应 UseCase
        2. PermissionEngine 根据 action 判断权限
        3. AuditEngine 根据 action 记录审计日志
        4. WorkflowEngine / ControlEngine 可以根据 action 触发规则

    示例：
        action="business.submit"
    """

    resource_ref: ResourceRef
    """
    主资源引用。

    resource_ref 表示这次动作主要操作哪个资源。

    例如：

        提交事前支出申请：
            resource_ref = ResourceRef(type="business", id=10001)

        审批任务：
            resource_ref = ResourceRef(type="task", id=50001)

        保存表单：
            resource_ref = ResourceRef(type="form", id=30001)

        下载文件：
            resource_ref = ResourceRef(type="file", id=90001)

    注意：
        resource_ref 只是引用，不是完整资源数据。

        它通常只包含：
            - type：资源类型
            - id：资源 ID

        真正的资源数据需要由对应 Engine 或 ResourceResolver 加载。

    为什么叫 resource_ref？
        因为它是 Resource Reference，表示“资源引用”，
        而不是已经解析完成的 Resource 对象。

    如果一个 UseCase 需要多个资源：
        resource_ref 表示主资源；
        其他资源可以放在 context、data 或 related_resources 中。
    """

    context: RequestContext
    """
    请求上下文。

    context 表示这次动作发生在什么业务现场中。

    常见字段包括：
        - actor_id：当前操作人
        - business_id：当前业务事项 ID
        - business_type：当前业务类型
        - task_id：当前任务 ID
        - workflow_id：当前流程实例 ID
        - node_id：当前流程节点 ID
        - request_id：请求 ID
        - trace_id：链路追踪 ID
        - source：请求来源
        - extra：扩展上下文

    context 的作用：
        1. PermissionEngine 用它判断当前用户能不能操作
        2. WorkflowEngine 用它判断当前任务和节点
        3. AuditEngine 用它记录谁在什么场景下操作
        4. FormEngine / DocumentEngine 用它加载业务类型对应的 Schema
        5. LogEngine 用它串联请求链路

    示例：
        RequestContext(
            actor_id=1,
            business_id=10001,
            business_type="pre_expense_apply",
            task_id=50001,
            source="web"
        )
    """

    data: dict[str, Any] = field(default_factory=dict)
    """
    动作参数。

    data 存放这次动作需要携带的业务数据。

    不同 action 对 data 的要求不同。

    示例一：提交申请

        action = "business.submit"

        data = {
            "comment": "提交申请"
        }

    示例二：保存表单

        action = "form.save"

        data = {
            "values": {
                "amount": 3000,
                "reason": "参加会议",
                "budgetSubject": "差旅费"
            }
        }

    示例三：审批任务

        action = "task.approve"

        data = {
            "comment": "同意",
            "signatureId": 123
        }

    示例四：文件绑定

        action = "file.bind"

        data = {
            "targetResource": {
                "type": "business",
                "id": 10001
            }
        }

    设计原则：
        1. data 只放本次动作需要的参数
        2. 不要把完整上下文都塞进 data
        3. 用户身份、业务 ID、任务 ID 应优先放 context
        4. 主资源应放 resource_ref
        5. 其他关联资源可以放 data 或 related_resources

    使用 default_factory=dict 的原因：
        避免多个 ResourceCommand 实例共享同一个默认字典。
    """

    options: dict[str, Any] = field(default_factory=dict)
    """
    执行选项。

    options 用来控制这次动作的执行方式，
    不属于核心业务数据。

    常见选项：

        {
            "dryRun": true
        }
        表示试运行，只校验不真正落库。

        {
            "validateOnly": true
        }
        表示只做校验，不执行核心动作。

        {
            "withWorkspace": true
        }
        表示执行完成后返回最新工作台数据。

        {
            "withResource": true
        }
        表示执行完成后返回最新资源详情。

        {
            "ignoreWarnings": true
        }
        表示忽略 warning 级别提示继续执行。

    data 和 options 的区别：

        data:
            是业务参数。
            例如 comment、values、reason。

        options:
            是执行控制参数。
            例如 dryRun、withWorkspace、validateOnly。

    使用 default_factory=dict 的原因：
        避免多个 ResourceCommand 实例共享同一个默认字典。
    """
