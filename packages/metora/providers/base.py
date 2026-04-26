from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    """
    Adapter 执行结果对象。

    所有 Adapter 调用外部服务后，都应该返回统一的 AdapterResult，
    这样 Engine 不需要关心具体第三方平台的返回格式。

    例如：
        - 企业微信返回 errcode / errmsg
        - 飞书返回 code / msg
        - OSS 返回 request_id
        - 邮件服务返回 message_id

    AdapterResult 会把这些不同格式统一成：
        - ok：是否成功
        - code：结果编码
        - message：结果说明
        - raw：原始返回数据
    """

    ok: bool
    """
    是否执行成功。

    True:
        Adapter 调用成功。

    False:
        Adapter 调用失败。

    示例：
        ok=True
        ok=False
    """

    code: str
    """
    结果编码。

    成功时一般可以是：
        "OK"

    失败时可以是：
        "WECHAT_SEND_FAILED"
        "FEISHU_TOKEN_EXPIRED"
        "OSS_UPLOAD_FAILED"
        "CONFIG_INVALID"

    code 适合用于程序判断和日志检索。
    """

    message: str
    """
    结果描述。

    主要给开发者、运维人员或日志系统查看。

    示例：
        "Adapter is healthy"
        "企业微信发送成功"
        "access_token 已过期"
        "缺少必要配置 app_id"
    """

    raw: dict[str, Any] = field(default_factory=dict)
    """
    第三方服务的原始返回。

    用于调试、审计、排查问题。

    示例：
        {
            "errcode": 0,
            "errmsg": "ok"
        }

    注意：
        raw 里不要保存敏感信息，例如密钥、token、密码。
        如果第三方返回中包含敏感字段，Adapter 应该先脱敏再写入 raw。

    使用 default_factory=dict 是为了避免多个实例共享同一个默认字典。
    """


class AdapterBase(ABC):
    """
    Adapter 基类。

    Adapter 是 Metora 用来对接外部实现的标准扩展点。

    例如：
        - NotificationAdapter：对接企业微信、飞书、邮件、短信
        - StorageAdapter：对接 OSS、MinIO、本地文件系统
        - ExportAdapter：对接 PDF / DOCX 导出服务
        - KeyProviderAdapter：对接 KMS、环境变量、数据库密钥
        - LogSinkAdapter：对接 ELK、Loki、文件日志

    设计目标：
        Engine 只依赖 AdapterBase 定义的统一接口，
        不直接依赖具体第三方 SDK 或服务。

    例如：
        NotificationEngine 不应该直接调用企业微信 API，
        而是调用 WeChatNotificationAdapter。
    """

    name: str = "base"
    """
    Adapter 名称。

    用于在 Registry 中注册和查找具体 Adapter。

    示例：
        "wechat"
        "feishu"
        "email"
        "oss"
        "minio"
        "local"

    注册示例：
        registry.register_adapter(
            capability="notification",
            name="wechat",
            adapter=WeChatNotificationAdapter()
        )

    获取示例：
        registry.get_adapter("notification", "wechat")
    """

    capability: str = "base"
    """
    Adapter 能力类型。

    用于区分 Adapter 属于哪一类能力。

    示例：
        "notification"  通知能力
        "storage"       文件存储能力
        "export"        文档导出能力
        "key_provider"  密钥提供能力
        "log_sink"      日志输出能力

    name + capability 一起构成 Adapter 的唯一定位。

    例如：
        capability="notification", name="wechat"
        表示企业微信通知适配器。

        capability="storage", name="oss"
        表示 OSS 文件存储适配器。
    """

    def validate_config(self) -> None:
        """
        校验 Adapter 配置是否完整、合法。

        适合检查：
            - app_id 是否存在
            - app_secret 是否存在
            - endpoint 是否正确
            - bucket 是否配置
            - token 是否可用
            - 必填参数是否缺失

        什么时候调用：
            1. Adapter 初始化后
            2. 系统启动时
            3. 管理后台保存配置后
            4. health_check 前

        成功：
            不返回任何内容。

        失败：
            建议抛出 ValueError 或自定义 ConfigError。

        示例：
            def validate_config(self):
                if not self.app_id:
                    raise ValueError("app_id is required")

                if not self.app_secret:
                    raise ValueError("app_secret is required")

        默认行为：
            BaseAdapter 不做任何校验。
            子类可以按需覆盖。
        """
        pass

    def health_check(self) -> ProviderResult:
        """
        检查 Adapter 当前是否可用。

        适合用于：
            - 系统启动检查
            - 管理后台测试连接
            - 运维健康检查
            - 故障排查
            - 定时巡检

        不同 Adapter 的检查方式不同：

            NotificationAdapter:
                可以检查第三方 token 是否有效。

            StorageAdapter:
                可以检查 bucket 是否可访问。

            ExportAdapter:
                可以检查导出服务是否在线。

            KeyProviderAdapter:
                可以检查密钥是否可读取。

        返回：
            AdapterResult

        成功示例：
            AdapterResult(
                ok=True,
                code="OK",
                message="Adapter is healthy",
            )

        失败示例：
            AdapterResult(
                ok=False,
                code="HEALTH_CHECK_FAILED",
                message="无法连接企业微信服务",
                raw={...}
            )

        默认行为：
            直接返回健康状态。
            子类如果有真实连接检查需求，应覆盖该方法。
        """
        return ProviderResult(
            ok=True,
            code="OK",
            message="Adapter is healthy",
        )