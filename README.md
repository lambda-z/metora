
# Metora - 资源驱动的 Python 业务运行时框架

Metora — Resource-driven business runtime for Python.

Metora 是一个资源驱动的 Python 业务运行时框架，用于构建企业 OA、事业单位内控、审批流、动态表单、在线文档、任务协同和业务事项管理系统。它的核心哲学是：万物皆资源，动作皆命令，能力皆引擎，业务皆用例，差异皆配置，实现皆 Provider。

Metora 是资源驱动的 Python 业务运行时：以 Resource 表达对象，以 Command 表达动作，以 UseCase 编排业务，以 Engine 提供能力，以 Provider 接入实现，以 Schema 和 Hook 承载差异。

# Installation
```bash

```

# 1. Registry

## register_provider
```python
def register_provider(self, capability: str, name: str, adapter: Any) -> None:
    self.providers[(capability, name)] = adapter
```

## register_engine
```python
def register_engine(self, name: str, engine: Any) -> None:
    ...
```

## register_usecase_class
```python
def register_usecase_class(self, action: str, usecase: Type[BaseUseCase]) -> None:
    self.usecases[action] = usecase
```

# 2. Provider

# 3. Engine

## How to extend Metora Engine?

- Inherit from `metora.engine.Engine` and implement the abstract methods.
- Define the engine adapter by inheriting from `metora.adapter.AdapterBase` and implement the abstract methods.
- In your engine, you can use the adapter to interact with external systems or services.
- And you can also define provider, which is a callable that can be used to provide data or functionality to the engine.


# 默认Engine及能力

## 3.1. NotificationEngine
- Send Message

```python
def send(self, channel: str, message: NotificationMessage):
    ...
```

## 3.2. WorkflowEngine

WorkflowEngine 是 Metora 中负责流程定义、流程实例、节点流转和任务生成的引擎，可用于实现审批流、办理流、归档流、整改流等业务流程。
WorkflowEngine 是流程流转引擎，审批流是它最典型的使用场景。

## 3.3 FileEngine

## 3.4 AuditEngine

## 3.5 AnalyticsEngine
AnalyticsEngine 是 Metora 的产品行为分析引擎，用于记录用户如何使用 Resource、Action、Task、Form、Conversation 等能力；具体写入数据库、Kafka、PostHog、神策等，由 AnalyticsProvider 实现。

## 3.6 PermissionEngine


## 3.7 OutboxEngine
OutboxEngine 是 Metora 的事件发件箱引擎，负责把业务动作产生的事件可靠地记录下来，并追踪这些事件是否已经发布到 Stream / Worker / 外部系统。

**职责**：
- 创建事件记录
- 查询待发布事件
- 标记事件发布中
- 标记事件发布成功
- 标记事件发布失败
- 记录重试次数
- 记录错误原因
- 计算下次重试时间
- 把事件交给 StreamProvider 发布

# 4. UseCase


# 5. Core
