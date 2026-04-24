from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from engines.base import BaseEngine


# =========================================================
# Actor
# =========================================================

@dataclass
class Actor:
    """
    Actor 是 Metora 中的“操作者”。

    为什么不直接叫 User？
        因为操作者不一定永远是系统用户，也可能是：
            - 普通用户
            - 管理员
            - 系统任务
            - 第三方 API Client
            - 定时任务
            - 机器人

    所以在 Metora Core 中建议使用 Actor，
    而不是直接绑定具体 Web 框架里的 User 模型。
    """

    id: str | int
    """
    操作者 ID。

    如果 actor_type = "user"，通常就是用户 ID。
    如果 actor_type = "system"，可以是 "system"。
    如果 actor_type = "api_client"，可以是 client_id。
    """

    actor_type: str = "user"
    """
    操作者类型。

    常见值：
        user
        system
        api_client
        robot
    """

    name: str | None = None
    """
    操作者名称。

    例如：
        张三
        系统任务
        外部接口客户端
    """

    roles: list[str] = field(default_factory=list)
    """
    角色编码列表。

    示例：
        ["employee"]
        ["department_manager"]
        ["finance", "internal_control_admin"]
    """

    permissions: list[str] = field(default_factory=list)
    """
    显式权限编码列表。

    示例：
        ["business.create", "audit.view", "permission.manage"]

    注意：
        大多数情况下，权限可以由角色推导。
        这个字段适合做额外授权或缓存结果。
    """

    department_id: str | int | None = None
    """
    所属部门 ID。
    """

    organization_id: str | int | None = None
    """
    所属组织 / 单位 ID。
    """

    position: str | None = None
    """
    岗位 / 职位。

    示例：
        manager
        finance_staff
        internal_control_officer
    """

    metadata: dict[str, Any] = field(default_factory=dict)
    """
    扩展信息。

    可以放：
        - 手机号
        - 邮箱
        - 企业微信 user_id
        - 飞书 open_id
        - 是否部门负责人
        - 外部系统映射 ID
    """

    def has_role(self, role: str) -> bool:
        """
        判断 Actor 是否拥有某个角色。
        """
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """
        判断 Actor 是否拥有某个显式权限。
        """
        return permission in self.permissions

    @property
    def is_system(self) -> bool:
        """
        是否为系统操作者。
        """
        return self.actor_type == "system"

    @property
    def is_admin(self) -> bool:
        """
        是否为管理员。

        这里用角色判断。
        你也可以根据项目习惯改成：
            super_admin
            system_admin
            admin
        """
        return "admin" in self.roles or "super_admin" in self.roles


# =========================================================
# Identity Persistence Provider
# =========================================================

class IdentityPersistenceProvider(Protocol):
    """
    Identity 持久化协议。

    IdentityEngine 不直接依赖用户表、角色表、部门表，
    而是通过这个协议获取身份信息。

    Django / SQLAlchemy / 现有组织架构系统 / 企业微信通讯录，
    都可以通过实现这个协议接入。
    """

    def get_actor(self, actor_id: str | int) -> Actor:
        """
        根据 actor_id 获取 Actor。
        """
        ...

    def get_roles(self, actor_id: str | int) -> list[str]:
        """
        获取 Actor 的角色列表。
        """
        ...

    def get_permissions(self, actor_id: str | int) -> list[str]:
        """
        获取 Actor 的显式权限列表。
        """
        ...

    def get_department_id(self, actor_id: str | int) -> str | int | None:
        """
        获取 Actor 所属部门 ID。
        """
        ...

    def is_department_manager(
        self,
        actor_id: str | int,
        department_id: str | int,
    ) -> bool:
        """
        判断 Actor 是否为某个部门负责人。
        """
        ...


# =========================================================
# Identity Engine
# =========================================================

class IdentityEngine(BaseEngine):
    """
    IdentityEngine：身份引擎。

    核心职责：
        1. 解析当前操作者 Actor
        2. 获取角色
        3. 获取权限
        4. 获取部门 / 组织信息
        5. 判断岗位关系，例如是否部门负责人
        6. 为 PermissionEngine 提供身份基础

    它不负责：
        - 判断某个动作是否允许执行：PermissionEngine
        - 执行业务动作：UseCase
        - 管理具体用户表：PersistenceProvider
    """

    engine_name = "identity"

    def __init__(
        self,
        persistence: IdentityPersistenceProvider | None = None,
        registry=None,
    ):
        super().__init__(registry=registry)
        self.persistence = persistence

    def initialize(self) -> None:
        """
        初始化 IdentityEngine。

        如果项目强依赖 IdentityEngine 查询真实用户，
        则应该配置 persistence。

        但为了方便测试，persistence 可以为空。
        """
        pass

    def get_actor(self, actor_id: str | int | None) -> Actor:
        """
        获取当前操作者。

        如果 actor_id 为空，返回 anonymous Actor。
        如果配置了 persistence，则从 persistence 中读取真实身份。
        如果没有配置 persistence，则返回一个最小 Actor。
        """

        if actor_id is None:
            return Actor(
                id="anonymous",
                actor_type="anonymous",
                name="Anonymous",
                roles=[],
                permissions=[],
            )

        if self.persistence:
            return self.persistence.get_actor(actor_id)

        return Actor(
            id=actor_id,
            actor_type="user",
            roles=[],
            permissions=[],
        )

    def get_roles(self, actor_id: str | int) -> list[str]:
        """
        获取 Actor 的角色列表。
        """

        if self.persistence:
            return self.persistence.get_roles(actor_id)

        return []

    def get_permissions(self, actor_id: str | int) -> list[str]:
        """
        获取 Actor 的显式权限列表。
        """

        if self.persistence:
            return self.persistence.get_permissions(actor_id)

        return []

    def get_department_id(self, actor_id: str | int) -> str | int | None:
        """
        获取 Actor 所属部门 ID。
        """

        if self.persistence:
            return self.persistence.get_department_id(actor_id)

        return None

    def is_department_manager(
        self,
        actor_id: str | int,
        department_id: str | int,
    ) -> bool:
        """
        判断 Actor 是否为某个部门负责人。
        """

        if self.persistence:
            return self.persistence.is_department_manager(
                actor_id=actor_id,
                department_id=department_id,
            )

        return False

    def validate(self, actor_id: str | int | None = None, *args, **kwargs) -> dict[str, Any]:
        """
        校验身份是否有效。

        返回结构化结果，方便 UseCase / PermissionEngine 使用。
        """

        actor = self.get_actor(actor_id)

        if actor.actor_type == "anonymous":
            return {
                "passed": False,
                "code": "ANONYMOUS_ACTOR",
                "message": "未识别的操作者",
                "actor": actor,
            }

        return {
            "passed": True,
            "code": "OK",
            "message": "身份有效",
            "actor": actor,
        }

    def get_state(self, actor_id: str | int | None = None, *args, **kwargs) -> dict[str, Any]:
        """
        获取 Actor 当前身份状态。

        适合用于：
            - 当前用户信息接口
            - 权限调试
            - 工作台初始化
        """

        actor = self.get_actor(actor_id)

        return {
            "actorId": actor.id,
            "actorType": actor.actor_type,
            "name": actor.name,
            "roles": actor.roles,
            "permissions": actor.permissions,
            "departmentId": actor.department_id,
            "organizationId": actor.organization_id,
            "position": actor.position,
            "isAdmin": actor.is_admin,
        }

    def get_available_actions(self, actor_id: str | int | None = None, *args, **kwargs) -> list[str]:
        """
        IdentityEngine 自身通常不直接暴露业务动作。

        如果后期你有身份管理后台，可以返回：
            - identity.view
            - identity.update_profile
            - identity.sync_org
        """

        actor = self.get_actor(actor_id)

        if actor.is_admin:
            return [
                "identity.view",
                "identity.sync",
                "identity.manage",
            ]

        if actor.actor_type == "user":
            return [
                "identity.view",
                "identity.update_profile",
            ]

        return []
