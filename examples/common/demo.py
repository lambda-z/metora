from core.commands import ResourceCommand, ResourceRef, RequestContext
from core.registry import MetoraRegistry
from core.runtime import MetoraRuntime

registry = MetoraRegistry()
runtime = MetoraRuntime(registry)

command = ResourceCommand(
    action="business.submit",
    resource=ResourceRef(type="business", id=1),
    context=RequestContext(actor_id=1),
)


if __name__ == '__main__':

    result = runtime.execute(command)
    print(result.to_dict())
