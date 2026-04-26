from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ActionResultCode(StrEnum):
    """
    ActionResult 的标准结果编码。

    code 用于给程序判断本次动作的执行结果类型，
    比 message 更稳定，适合前端、日志、监控、测试代码使用。

    例如：
        OK:
            执行成功。

        ACTION_NOT_SUPPORTED:
            当前 action 没有注册对应 UseCase，或者框架不支持该动作。

    后续可以继续扩展：
        BAD_REQUEST
        PERMISSION_DENIED
        VALIDATION_FAILED
        RESOURCE_NOT_FOUND
        INTERNAL_ERROR
    """

    OK = "OK"
    """
    动作执行成功。
    """

    ACTION_NOT_SUPPORTED = "ACTION_NOT_SUPPORTED"
    """
    动作不支持。

    常见原因：
        1. action 没有注册到 MetoraRegistry
        2. action 拼写错误
        3. 当前模块没有安装
        4. 当前业务版本不支持该动作
    """


@dataclass
class ActionResult:
    """
    ActionResult 是 Metora 中统一的动作执行结果。

    所有 UseCase 执行完成后，都应该返回 ActionResult。

    它用于描述：
        1. 动作是否成功
        2. 结果编码是什么
        3. 给用户或开发者看的消息是什么
        4. 本次动作影响了哪些资源
        5. 前端需要刷新哪些区域
        6. 是否产生了事件
        7. HTTP 层应该返回什么状态码

    它是框架内部执行结果和 Web Response 之间的桥梁。

    执行链路通常是：

        ResourceCommand
            ↓
        MetoraRuntime
            ↓
        UseCase
            ↓
        ActionResult
            ↓
        Django / FastAPI / Flask Response
    """

    ok: bool
    """
    是否执行成功。

    True:
        表示动作成功完成。

    False:
        表示动作失败，具体失败原因由 code 和 message 描述。

    示例：
        ok=True
        ok=False
    """

    code: ActionResultCode
    """
    标准结果编码。

    用于程序判断结果类型。

    不建议前端只通过 message 判断结果，
    因为 message 可能会随着语言和文案变化。

    示例：
        ActionResultCode.OK
        ActionResultCode.ACTION_NOT_SUPPORTED
    """

    message: str
    """
    结果说明文案。

    通常用于：
        1. 返回给前端展示
        2. 写入日志
        3. 开发调试

    示例：
        "提交成功"
        "动作不支持"
        "表单校验未通过"
        "你没有权限执行该操作"
    """

    action: str | None = None
    """
    本次执行的动作名称。

    通常与 ResourceCommand.action 保持一致。

    示例：
        business.submit
        task.approve
        form.save
        document.finalize

    用途：
        1. 前端确认本次执行的是哪个动作
        2. 日志和调试更清晰
        3. 多动作批量执行时方便区分结果
    """

    resource: dict[str, Any] | None = None
    """
    本次动作的主资源信息。

    通常是一个简化后的 Resource 视图，
    方便前端更新当前页面或列表状态。

    示例：
        {
            "type": "business",
            "id": 10001,
            "title": "张三的事前支出申请",
            "status": "submitted"
        }

    注意：
        这里不建议返回完整业务数据。
        完整详情可以放在 result 中，或者由前端重新拉取。
    """

    result: dict[str, Any] = field(default_factory=dict)
    """
    本次动作的业务结果数据。

    不同 action 返回的 result 可以不同。

    示例一：business.submit

        {
            "businessId": 10001,
            "nextTaskId": 50002,
            "nextNodeId": "manager_approve"
        }

    示例二：form.save

        {
            "formId": 30001,
            "updatedAt": "2026-04-24T10:30:00"
        }

    示例三：file.upload

        {
            "fileId": 90001,
            "downloadUrl": "..."
        }

    设计原则：
        1. resource 放主资源概览
        2. result 放动作执行后的详细结果
        3. 不要把无关的大对象塞进 result
    """

    effects: dict[str, bool] = field(default_factory=dict)
    """
    本次动作影响了哪些领域能力或资源类型。

    用于告诉前端或后续系统：
        哪些部分发生了变化。

    示例：
        {
            "business": true,
            "workflow": true,
            "task": true,
            "form": false,
            "document": false
        }

    常见 key：
        business
        workflow
        task
        form
        document
        file
        notification
        permission
        audit

    用途：
        1. 前端决定是否刷新对应区域
        2. 后续事件处理判断影响范围
        3. 日志和调试更清楚
    """

    refresh: dict[str, bool] = field(default_factory=dict)
    """
    给前端的刷新建议。

    effects 表示“系统里哪些东西变了”，
    refresh 表示“前端最好刷新哪些视图”。

    示例：
        {
            "workspace": true,
            "todos": true,
            "list": true,
            "resource": false
        }

    常见 key：
        workspace   当前工作台
        todos       待办列表
        list        当前业务列表
        resource    当前资源详情
        timeline    流程时间线
        notifications 消息列表

    注意：
        refresh 只是建议。
        前端可以根据自身状态管理策略决定如何处理。
    """

    events: list[dict[str, Any]] = field(default_factory=list)
    """
    本次动作产生的事件列表。

    这些事件通常来自 Outbox / EventBus，
    用于后续异步处理。

    示例：
        [
            {
                "type": "BusinessSubmitted",
                "id": "event_001",
                "status": "pending"
            },
            {
                "type": "TaskCreated",
                "id": "event_002",
                "status": "pending"
            }
        ]

    事件可以触发：
        1. 通知发送
        2. 搜索索引更新
        3. 审计归档
        4. 外部系统同步
        5. PDF 异步生成
    """

    http_status: int = 200
    """
    建议 HTTP 状态码。

    ActionResult 本身是框架结果，
    但 Web Adapter 可以使用 http_status 生成 HTTP Response。

    常见值：
        200 成功
        400 请求参数错误
        403 无权限
        404 资源不存在
        409 业务状态冲突 / 内控阻断
        500 系统异常

    示例：
        FastAPI:
            return JSONResponse(
                content=result.to_dict(),
                status_code=result.http_status
            )

        Django REST Framework:
            return Response(
                result.to_dict(),
                status=result.http_status
            )
    """

    def to_dict(self) -> dict[str, Any]:
        """
        将 ActionResult 转换为普通 dict。

        主要用于：
            1. 返回 HTTP JSON Response
            2. 写日志
            3. 测试断言
            4. 序列化传输

        返回示例：
            {
                "ok": true,
                "code": "OK",
                "message": "提交成功",
                "action": "business.submit",
                "resource": {
                    "type": "business",
                    "id": 10001,
                    "status": "submitted"
                },
                "result": {
                    "businessId": 10001,
                    "nextTaskId": 50002
                },
                "effects": {
                    "business": true,
                    "workflow": true
                },
                "refresh": {
                    "workspace": true,
                    "todos": true
                },
                "events": []
            }

        注意：
            code 是 StrEnum。
            在 Python 中 StrEnum 本身可以作为字符串使用，
            但如果你希望完全转成普通字符串，也可以写：
                "code": self.code.value
        """
        return {
            "ok": self.ok,
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "resource": self.resource,
            "result": self.result,
            "effects": self.effects,
            "refresh": self.refresh,
            "events": self.events,
        }
