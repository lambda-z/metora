from __future__ import annotations

from typing import Any


class BaseEngine:
    """
    Metora Engine 基类。

    Engine 是 Metora 中的“能力模块”。

    例如：
        - BusinessEngine：业务事项能力
        - WorkflowEngine：流程 / 任务流转能力
        - FormEngine：表单能力
        - DocumentEngine：文档能力
        - FileEngine：文件能力
        - PermissionEngine：权限判断能力
        - NotificationEngine：通知能力
        - AuditEngine：审计能力

    BaseEngine 不应该包含具体业务逻辑。
    它只提供所有 Engine 都可以遵循的统一生命周期和基础能力接口。

    子类可以根据自己的能力特点，选择性覆盖这些方法。
    """

    engine_name = "base"
    """
    Engine 的唯一名称。

    用途：
        1. 注册到 MetoraRegistry 时作为 key
        2. 日志、调试、审计时标识当前 Engine
        3. 通过 registry.get_engine(engine_name) 获取对应 Engine
        4. 加载 Schema / Config 时可用于匹配配置类型

    示例：
        class BusinessEngine(BaseEngine):
            engine_name = "business"

        class WorkflowEngine(BaseEngine):
            engine_name = "workflow"

        class NotificationEngine(BaseEngine):
            engine_name = "notification"
    """

    def __init__(self, registry=None):
        """
        初始化 Engine。

        参数：
            registry:
                Metora 的注册中心，通常是 MetoraRegistry 实例。

                registry 用来获取：
                    - 其他 Engine
                    - Adapter
                    - Hook
                    - Handler
                    - UseCase
                    - PersistenceProvider
                    - 配置对象

        为什么 Engine 需要 registry？
            因为 Engine 有时需要调用框架中已经注册的扩展能力。

            例如：
                NotificationEngine 需要从 registry 中获取 notification adapter：
                    registry.get_adapter("notification", "wechat")

                FileEngine 需要获取 storage adapter：
                    registry.get_adapter("storage", "oss")

                ControlEngine 需要获取 rule handler：
                    registry.get_handler("control_rule", "amount_limit")

        设计原则：
            1. registry 是可选的，方便单元测试。
            2. Engine 不应该过度依赖 registry。
            3. 如果依赖很强，优先通过构造函数显式注入依赖。
            4. registry 更适合用于插件化、适配器和扩展点查询。

        示例：
            engine = NotificationEngine(registry=registry)

        注意：
            BaseEngine 不会自动调用 initialize()。
            是否调用 initialize() 由 MetoraRuntime 或注册过程决定。
        """
        self.registry = registry

    def initialize(self) -> None:
        """
        Engine 初始化钩子。

        这个方法用于 Engine 被注册后、正式使用前的初始化工作。

        适合做什么：
            1. 注册默认 Handler
            2. 注册默认 Adapter
            3. 加载默认配置
            4. 检查必要依赖是否存在
            5. 初始化内部缓存
            6. 初始化外部客户端
            7. 做健康检查前的准备

        不适合做什么：
            1. 不建议在这里执行复杂业务逻辑
            2. 不建议在这里启动长时间阻塞任务
            3. 不建议在这里直接操作业务数据
            4. 不建议在这里发送通知、推进流程、修改状态

        示例：
            class ControlEngine(BaseEngine):
                engine_name = "control"

                def initialize(self):
                    self.register_rule_handler("required_fields", RequiredFieldsHandler())
                    self.register_rule_handler("amount_limit", AmountLimitHandler())

            class NotificationEngine(BaseEngine):
                engine_name = "notification"

                def initialize(self):
                    if not self.registry:
                        raise RuntimeError("NotificationEngine requires registry")

        调用时机建议：
            registry.register_engine("notification", engine)
            engine.initialize()

        默认行为：
            BaseEngine.initialize() 什么都不做。
            子类可以按需覆盖。
        """
        pass

    def validate(self, *args, **kwargs) -> Any:
        """
        校验当前 Engine 相关的输入、配置、状态或动作是否有效。

        validate 是一个通用校验入口。
        不同 Engine 对 validate 的含义可以不同。

        常见用途：
            1. 校验输入数据是否合法
            2. 校验资源当前状态是否允许执行动作
            3. 校验 Schema / Rule / Config 是否正确
            4. 校验外部 Adapter 配置是否完整
            5. 校验某个业务动作是否满足前置条件

        示例一：FormEngine 校验表单数据
            form_engine.validate(
                schema=form_schema,
                values={
                    "amount": 3000,
                    "reason": "参加会议"
                }
            )

            返回：
                {
                    "passed": True,
                    "errors": []
                }

        示例二：WorkflowEngine 校验任务能否审批
            workflow_engine.validate(
                action="task.approve",
                task=task_instance,
                actor_id=1
            )

        示例三：DocumentEngine 校验文档能否定稿
            document_engine.validate(
                action="document.finalize",
                document=document_instance
            )

        返回值建议：
            可以返回 None，表示无校验结果或默认通过。

            更推荐子类返回结构化结果，例如：
                {
                    "passed": True,
                    "errors": []
                }

            或者定义专门的 ValidateResult：
                ValidateResult(
                    passed=True,
                    errors=[]
                )

        是否应该抛异常？
            两种方式都可以，但建议统一风格。

            方式一：返回校验结果
                适合表单校验、内控校验，需要把错误返回给前端。

            方式二：抛出异常
                适合配置错误、系统错误、非法状态。

        默认行为：
            BaseEngine.validate() 返回 None。
            表示基类不提供任何校验逻辑。
        """
        return None

    def get_state(self, *args, **kwargs) -> Any:
        """
        获取当前 Engine 管理对象的状态。

        get_state 用来回答：
            “当前资源 / 当前流程 / 当前表单 / 当前文档处于什么状态？”

        不同 Engine 的 state 含义不同。

        例如：

        1. BusinessEngine
            获取业务事项状态：
                draft
                approving
                completed
                archived

            示例：
                business_engine.get_state(business_id=10001)

            返回：
                {
                    "status": "approving",
                    "statusText": "审批中",
                    "businessType": "pre_expense_apply"
                }

        2. WorkflowEngine
            获取流程状态：
                当前节点
                当前任务
                是否完成
                流程时间线

            示例：
                workflow_engine.get_state(business_id=10001)

            返回：
                {
                    "currentNodeId": "manager_approve",
                    "currentTaskId": 50001,
                    "completed": False
                }

        3. FormEngine
            获取表单状态：
                draft
                saved
                frozen
                invalid

            示例：
                form_engine.get_state(form_id=30001)

        4. DocumentEngine
            获取文档状态：
                editing
                finalized
                exported
                archived

        5. NotificationEngine
            获取通知状态：
                unread
                read
                sent
                failed

        适合使用场景：
            1. 构建工作台页面
            2. 判断前端按钮是否可用
            3. 状态流转前检查
            4. 审计展示
            5. 查询当前业务进度

        返回值建议：
            可以返回任意结构，但建议返回 dict 或明确的 State DTO。

        默认行为：
            BaseEngine.get_state() 返回 None。
            表示基类不知道具体状态。
        """
        return None

    def get_available_actions(self, *args, **kwargs) -> list[str]:
        """
        获取当前状态下可执行的动作列表。

        这个方法用于回答：
            “当前用户 / 当前资源 / 当前状态下，可以做哪些动作？”

        它通常会结合：
            1. 当前资源状态
            2. 当前用户身份
            3. 当前流程节点
            4. 当前任务状态
            5. 权限策略
            6. 内控规则
            7. 业务配置

        示例一：BusinessEngine
            business_engine.get_available_actions(
                context=context,
                business_id=10001
            )

            可能返回：
                [
                    "business.submit",
                    "business.withdraw",
                    "form.save"
                ]

        示例二：WorkflowEngine
            workflow_engine.get_available_actions(
                context=context,
                task_id=50001
            )

            可能返回：
                [
                    "task.approve",
                    "task.reject",
                    "task.return"
                ]

        示例三：DocumentEngine
            document_engine.get_available_actions(
                context=context,
                document_id=70001
            )

            可能返回：
                [
                    "document.edit",
                    "document.finalize",
                    "document.export_pdf"
                ]

        和 PermissionEngine 的关系：
            get_available_actions 可以调用 PermissionEngine 过滤权限。

            例如：
                资源状态允许 document.edit
                但当前用户没有权限
                那么最终不应该返回 document.edit

        和前端的关系：
            工作台接口可以把这个方法的结果返回给前端，
            用于渲染按钮。

            示例：
                {
                    "availableActions": [
                        {
                            "key": "task.approve",
                            "label": "通过",
                            "type": "primary"
                        },
                        {
                            "key": "task.reject",
                            "label": "驳回",
                            "type": "danger"
                        }
                    ]
                }

        注意：
            前端隐藏按钮不等于安全。
            即使某个 action 没返回，后端执行 action 时仍然必须再次校验权限。

        返回值：
            默认返回动作 key 列表：
                ["business.submit", "task.approve"]

            后期也可以扩展成动作对象：
                [
                    {
                        "key": "task.approve",
                        "label": "通过",
                        "type": "primary"
                    }
                ]

            如果要支持动作对象，建议新增方法：
                get_available_action_items()

            或者统一返回 list[ActionDescriptor]。

        默认行为：
            BaseEngine.get_available_actions() 返回空列表。
            表示当前 Engine 默认不暴露任何可执行动作。
        """
        return []