from providers.notification.base import NotificationMessage
from core.commands import ResourceCommand, ResourceRef, RequestContext
from core.registry import MetoraRegistry
from core.results import ActionResult, ActionResultCode
from core.runtime import MetoraRuntime
from engines.notification import NotificationEngine
from usecases.base import BaseUseCase


# 实现一个UseCase
class DemoUseCase(BaseUseCase):

    def execute(self, command: ResourceCommand) -> ActionResult:

        # 获取engine
        notification_engine: NotificationEngine = self.metora.engine.notification
        print(f"Got notification_engine: {notification_engine}")
        notification_engine.send("wechat", NotificationMessage(
            receiver="1234567890",
            title="Demo notification",
            content="This is a demo notification",
        ))

        return ActionResult(
            ok=True,
            code=ActionResultCode.OK,
            message="Demo use case executed successfully",
            action=command.action,
            resource={
                "type": command.resource_ref.type,
                "id": command.resource_ref.id,
                "status": "submitted",
            },
            result={
                "businessId": command.resource_ref.id,
                "nextNode": "manager_approve",
            },
            effects={
                "business": True,
                "workflow": True,
            }
        )

registry = MetoraRegistry()
registry.register_usecase_class("demo.submit", DemoUseCase)
registry.register_engine("notification", NotificationEngine(registry))


def run():
    command = ResourceCommand(
        action="demo.submit",
        resource_ref=ResourceRef(type="demo", id=1),
        context=RequestContext(actor_id=1),
    )
    runtime = MetoraRuntime(registry)
    result = runtime.execute(command)
    print(result.to_dict())


if __name__ == '__main__':

    run()


