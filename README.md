
# Metora - 资源驱动的 Python 业务运行时框架

Metora — Resource-driven business runtime for Python.

Metora 是一个资源驱动的 Python 业务运行时框架，用于构建企业 OA、事业单位内控、审批流、动态表单、在线文档、任务协同和业务事项管理系统。它的核心哲学是：万物皆资源，动作皆命令，能力皆引擎，业务皆用例，差异皆配置，实现皆 Provider。

Metora 是资源驱动的 Python 业务运行时：以 Resource 表达对象，以 Command 表达动作，以 UseCase 编排业务，以 Engine 提供能力，以 Provider 接入实现，以 Schema 和 Hook 承载差异。

# Registry

## Adapter

# Engine

## How to extend Metora Engine?

- 1. Inherit from `metora.engine.Engine` and implement the abstract methods.
- 2. Define the engine adapter by inheriting from `metora.adapter.AdapterBase` and implement the abstract methods.
- 3. In your engine, you can use the adapter to interact with external systems or services.
- 4. And you can also define provider, which is a callable that can be used to provide data or functionality to the engine.


# 默认Engine及能力

## 1. NotificationEngine
- Send Message

```python
def send(self, channel: str, message: NotificationMessage):
    ...
```

