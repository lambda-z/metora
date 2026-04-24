from core.commands import ResourceCommand, ResourceRef, RequestContext
from core.registry import MetoraRegistry
from core.results import ActionResult
from core.runtime import MetoraRuntime
from usecases.base import BaseUseCase


# 实现一个UseCase
class DemoUseCase(BaseUseCase):

    def execute(self, command: ResourceCommand) -> ActionResult:
        return ActionResult(
            ok=True,
            code="OK",
            message="Demo use case executed successfully",
            action=command.action,
            resource={
                "type": command.resource.type,
                "id": command.resource.id,
                "status": "submitted",
            },
            result={
                "businessId": command.resource.id,
                "nextNode": "manager_approve",
            },
            effects={
                "business": True,
                "workflow": True,
            }
        )

registry = MetoraRegistry()
registry.register_usecase_class("demo.submit", DemoUseCase)


def run():
    command = ResourceCommand(
        action="demo.submit",
        resource=ResourceRef(type="demo", id=1),
        context=RequestContext(actor_id=1),
    )
    runtime = MetoraRuntime(registry)
    result = runtime.execute(command)
    print(result.to_dict())


if __name__ == '__main__':

    run()


