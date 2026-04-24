from core.commands import ResourceCommand, ResourceRef, RequestContext
from core.registry import MetoraRegistry
from core.runtime import MetoraRuntime
from usecases.base import BaseUseCase


# 实现一个UseCase
class DemoUseCase(BaseUseCase):

    def execute(self, command):
        return {
            "message": f"Hello, {command.context.actor_id}! You have submitted business {command.resource.id}."
        }


registry = MetoraRegistry()

def run():
    command = ResourceCommand(
        action="business.submit",
        resource=ResourceRef(type="business", id=1),
        context=RequestContext(actor_id=1),
    )
    runtime = MetoraRuntime(registry)
    result = runtime.execute(command)
    print(result.to_dict())


if __name__ == '__main__':

    run()
