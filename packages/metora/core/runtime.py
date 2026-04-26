# metora/core/runtime.py
from packages.metora.core.commands import ResourceCommand
from packages.metora.core.context import MetoraContext
from packages.metora.core.results import ActionResult, ActionResultCode


class MetoraRuntime:
    def __init__(self, registry):
        self.registry = registry
        self.context = MetoraContext(registry)

    def execute(self, command: ResourceCommand) -> ActionResult:
        usecase_cls = self.registry.get_usecase_class(command.action)

        if not usecase_cls:
            return ActionResult(
                ok=False,
                code=ActionResultCode.ACTION_NOT_SUPPORTED,
                message=f"Unsupported action: {command.action}",
                action=command.action,
                http_status=400,
            )

        usecase = usecase_cls(metora=self.context)

        return usecase.run(command)
