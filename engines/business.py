from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from core.resources import Resource


# =========================================================
# BusinessInstance Protocol
# =========================================================

class BusinessInstanceProtocol(Protocol):
    """
    BusinessInstance 协议。

    用户可以使用 Metora 默认的 BusinessInstance，
    也可以使用自己项目里的业务表。

    只要实现这些字段和 to_resource() 方法，
    BusinessEngine 就可以正常使用。
    """

    id: str | int
    business_no: str | None
    business_type: str
    title: str
    status: str

    applicant_id: str | int | None
    department_id: str | int | None

    summary_data: dict[str, Any]

    created_by_id: str | int | None
    updated_by_id: str | int | None

    created_at: datetime | None
    updated_at: datetime | None

    def to_resource(self) -> Resource:
        ...


# =========================================================
# Business Persistence Provider
# =========================================================

class BusinessPersistenceProvider(Protocol):
    """
    Business 持久化协议。

    BusinessEngine 不直接操作数据库，
    只依赖这个协议。

    Django / SQLAlchemy / MongoDB / 用户自定义表，
    都可以通过实现这个协议接入。
    """

    def generate_business_no(self, business_type: str) -> str:
        """
        生成业务编号。

        例如：
            EXP-20260424-0001
            CONTRACT-20260424-0001
        """
        ...

    def create(
        self,
        *,
        business_no: str,
        business_type: str,
        title: str,
        status: str,
        applicant_id: str | int | None,
        department_id: str | int | None,
        summary_data: dict[str, Any],
        created_by_id: str | int | None,
        metadata: dict[str, Any] | None = None,
    ) -> BusinessInstanceProtocol:
        """
        创建 BusinessInstance。
        """
        ...

    def get(self, business_id: str | int) -> BusinessInstanceProtocol:
        """
        根据 ID 获取 BusinessInstance。
        """
        ...

    def update_status(
        self,
        *,
        business_id: str | int,
        status: str,
        updated_by_id: str | int | None = None,
    ) -> BusinessInstanceProtocol:
        """
        更新业务事项状态。
        """
        ...

    def update_summary(
        self,
        *,
        business_id: str | int,
        summary_data: dict[str, Any],
        updated_by_id: str | int | None = None,
        merge: bool = True,
    ) -> BusinessInstanceProtocol:
        """
        更新业务摘要数据。
        """
        ...

    def update_title(
        self,
        *,
        business_id: str | int,
        title: str,
        updated_by_id: str | int | None = None,
    ) -> BusinessInstanceProtocol:
        """
        更新业务标题。
        """
        ...

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        data_scope: Any | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[BusinessInstanceProtocol]:
        """
        查询业务事项列表。

        data_scope 可以是中立 DataScope，
        由具体 PersistenceProvider 自己编译成 ORM 查询条件。
        """
        ...


# =========================================================
# Business Context
# =========================================================

@dataclass
class BusinessContext:
    """
    BusinessEngine 使用的上下文。

    它可以由 ResourceCommand.context 转换而来。
    """

    actor_id: str | int | None = None
    department_id: str | int | None = None

    business_type: str | None = None

    request_id: str | None = None
    trace_id: str | None = None
    source: str | None = None

    extra: dict[str, Any] = field(default_factory=dict)


# =========================================================
# Business Engine Result
# =========================================================

@dataclass
class BusinessEngineResult:
    """
    BusinessEngine 内部返回结果。

    注意：
        这不是最终 API 响应。
        UseCase 会把它转换成 ActionResult。
    """

    ok: bool
    code: str
    message: str

    business: BusinessInstanceProtocol | None = None

    data: dict[str, Any] = field(default_factory=dict)


# =========================================================
# Business Engine
# =========================================================

class BusinessEngine:
    """
    BusinessEngine：业务事项引擎。

    核心职责：
        1. 创建业务事项 BusinessInstance
        2. 生成业务编号
        3. 维护事项状态
        4. 维护事项摘要 summary_data
        5. 撤回、取消、归档事项
        6. 获取事项 Resource 视图
        7. 查询业务事项列表

    不负责：
        - 表单字段保存：FormEngine
        - 审批流转：WorkflowEngine
        - 文件上传下载：FileEngine
        - 文档编辑定稿：DocumentEngine
        - 权限判断：PermissionEngine
        - 内控规则：ControlEngine
        - 审计留痕：AuditEngine
    """

    engine_name = "business"

    def __init__(
        self,
        persistence: BusinessPersistenceProvider,
        registry=None,
    ):
        self.persistence = persistence
        self.registry = registry

    # =====================================================
    # Create
    # =====================================================

    def create(
        self,
        *,
        context: BusinessContext,
        business_type: str,
        title: str,
        summary_data: dict[str, Any] | None = None,
        applicant_id: str | int | None = None,
        department_id: str | int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BusinessEngineResult:
        """
        创建一个业务事项。

        例如：
            创建事前支出申请
            创建出差申请
            创建合同审批事项

        创建后通常状态为 draft。
        """

        if not business_type:
            raise ValueError("business_type is required")

        if not title:
            raise ValueError("title is required")

        business_no = self.persistence.generate_business_no(business_type)

        business = self.persistence.create(
            business_no=business_no,
            business_type=business_type,
            title=title,
            status="draft",
            applicant_id=applicant_id or context.actor_id,
            department_id=department_id or context.department_id,
            summary_data=summary_data or {},
            created_by_id=context.actor_id,
            metadata=metadata or {},
        )

        return BusinessEngineResult(
            ok=True,
            code="OK",
            message="业务事项创建成功",
            business=business,
            data={
                "businessId": business.id,
                "businessNo": business.business_no,
                "businessType": business.business_type,
                "status": business.status,
            },
        )

    # =====================================================
    # Get
    # =====================================================

    def get(
        self,
        *,
        business_id: str | int,
    ) -> BusinessInstanceProtocol:
        """
        获取业务事项实例。
        """

        return self.persistence.get(business_id)

    def get_resource(
        self,
        *,
        business_id: str | int,
    ) -> Resource:
        """
        获取业务事项对应的 Resource 运行时视图。
        """

        business = self.persistence.get(business_id)
        return business.to_resource()

    # =====================================================
    # Status
    # =====================================================

    def update_status(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
        status: str,
    ) -> BusinessEngineResult:
        """
        更新业务事项状态。

        常见状态：
            draft
            submitted
            approving
            rejected
            returned
            completed
            archived
            cancelled
        """

        if not status:
            raise ValueError("status is required")

        business = self.persistence.update_status(
            business_id=business_id,
            status=status,
            updated_by_id=context.actor_id,
        )

        return BusinessEngineResult(
            ok=True,
            code="OK",
            message="业务状态更新成功",
            business=business,
            data={
                "businessId": business.id,
                "status": business.status,
            },
        )

    def mark_submitted(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
    ) -> BusinessEngineResult:
        """
        标记业务事项已提交。
        """

        return self.update_status(
            context=context,
            business_id=business_id,
            status="submitted",
        )

    def mark_approving(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
    ) -> BusinessEngineResult:
        """
        标记业务事项审批中。
        """

        return self.update_status(
            context=context,
            business_id=business_id,
            status="approving",
        )

    def mark_completed(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
    ) -> BusinessEngineResult:
        """
        标记业务事项已完成。
        """

        return self.update_status(
            context=context,
            business_id=business_id,
            status="completed",
        )

    def archive(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
    ) -> BusinessEngineResult:
        """
        归档业务事项。
        """

        return self.update_status(
            context=context,
            business_id=business_id,
            status="archived",
        )

    def cancel(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
    ) -> BusinessEngineResult:
        """
        取消业务事项。
        """

        return self.update_status(
            context=context,
            business_id=business_id,
            status="cancelled",
        )

    def withdraw(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
    ) -> BusinessEngineResult:
        """
        撤回业务事项。

        这里只处理事项状态。
        是否允许撤回，应由 UseCase 调用 PermissionEngine / WorkflowEngine 判断。
        """

        return self.update_status(
            context=context,
            business_id=business_id,
            status="withdrawn",
        )

    # =====================================================
    # Summary Data
    # =====================================================

    def update_summary(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
        summary_data: dict[str, Any],
        merge: bool = True,
    ) -> BusinessEngineResult:
        """
        更新业务事项摘要数据。

        summary_data 不是完整业务表单，
        而是用于列表、卡片、检索、工作台展示的关键字段快照。

        例如：
            {
                "amount": 3000,
                "expenseType": "meeting",
                "budgetSubject": "差旅费"
            }
        """

        if not isinstance(summary_data, dict):
            raise ValueError("summary_data must be a dict")

        business = self.persistence.update_summary(
            business_id=business_id,
            summary_data=summary_data,
            updated_by_id=context.actor_id,
            merge=merge,
        )

        return BusinessEngineResult(
            ok=True,
            code="OK",
            message="业务摘要更新成功",
            business=business,
            data={
                "businessId": business.id,
                "summaryData": business.summary_data,
            },
        )

    def sync_summary_from_values(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
        values: dict[str, Any],
        fields: list[str],
    ) -> BusinessEngineResult:
        """
        从表单 values 中提取部分字段，更新到 summary_data。

        适合在 SaveFormUseCase 中调用。

        示例：
            values = {
                "amount": 3000,
                "reason": "会议支出",
                "attachments": [...]
            }

            fields = ["amount", "reason"]

            最终 summary_data:
                {
                    "amount": 3000,
                    "reason": "会议支出"
                }
        """

        summary_data = {
            field: values.get(field)
            for field in fields
            if field in values
        }

        return self.update_summary(
            context=context,
            business_id=business_id,
            summary_data=summary_data,
            merge=True,
        )

    # =====================================================
    # Title
    # =====================================================

    def update_title(
        self,
        *,
        context: BusinessContext,
        business_id: str | int,
        title: str,
    ) -> BusinessEngineResult:
        """
        更新业务事项标题。
        """

        if not title:
            raise ValueError("title is required")

        business = self.persistence.update_title(
            business_id=business_id,
            title=title,
            updated_by_id=context.actor_id,
        )

        return BusinessEngineResult(
            ok=True,
            code="OK",
            message="业务标题更新成功",
            business=business,
            data={
                "businessId": business.id,
                "title": business.title,
            },
        )

    # =====================================================
    # List
    # =====================================================

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        data_scope: Any | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[BusinessInstanceProtocol]:
        """
        查询业务事项列表。

        filters:
            普通查询条件，例如：
                {
                    "business_type": "pre_expense_apply",
                    "status": "approving",
                    "keyword": "张三"
                }

        data_scope:
            权限系统返回的数据范围。
            例如：
                all
                self
                department
                participated

            BusinessEngine 不负责解释 data_scope。
            由具体 PersistenceProvider 决定如何编译。
        """

        return self.persistence.list(
            filters=filters or {},
            data_scope=data_scope,
            limit=limit,
            offset=offset,
        )

    # =====================================================
    # State & Actions
    # =====================================================

    def get_state(
        self,
        *,
        business_id: str | int,
    ) -> dict[str, Any]:
        """
        获取业务事项状态信息。
        """

        business = self.persistence.get(business_id)

        return {
            "businessId": business.id,
            "businessNo": business.business_no,
            "businessType": business.business_type,
            "title": business.title,
            "status": business.status,
            "summaryData": business.summary_data,
        }

    def get_available_actions(
        self,
        *,
        business_id: str | int,
    ) -> list[str]:
        """
        根据业务事项当前状态，返回可能的动作。

        注意：
            这里只根据状态给出基础动作。
            最终动作还需要 PermissionEngine 过滤。
        """

        business = self.persistence.get(business_id)

        status = business.status

        if status == "draft":
            return [
                "form.save",
                "business.submit",
                "business.cancel",
            ]

        if status in ["submitted", "approving"]:
            return [
                "business.withdraw",
            ]

        if status == "completed":
            return [
                "business.archive",
            ]

        if status == "archived":
            return [
                "business.view",
            ]

        return [
            "business.view",
        ]
