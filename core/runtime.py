from __future__ import annotations

from .commands import ResourceCommand
from .results import ActionResult
from .registry import (MetoraRegistry)


class MetoraRuntime:
    def __init__(self, registry: MetoraRegistry):
        self.registry = registry

    def execute(self, command: ResourceCommand) -> ActionResult:
        usecase = self.registry.get_usecase(command.action)

        if usecase is None:
            return ActionResult(
                ok=False,
                code="ACTION_NOT_SUPPORTED",
                message=f"Unsupported action: {command.action}",
                action=command.action,
                http_status=400,
            )

        try:
            return usecase.run(command)

        except PermissionError as error:
            return ActionResult(
                ok=False,
                code="PERMISSION_DENIED",
                message=str(error),
                action=command.action,
                http_status=403,
            )

        except ValueError as error:
            return ActionResult(
                ok=False,
                code="BAD_REQUEST",
                message=str(error),
                action=command.action,
                http_status=400,
            )

        except Exception as error:
            return ActionResult(
                ok=False,
                code="INTERNAL_ERROR",
                message=str(error),
                action=command.action,
                http_status=500,
            )
