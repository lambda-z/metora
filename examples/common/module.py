from typing import Any

from core.commands import ResourceCommand
from core.results import ActionResult
from usecases.base import BaseUseCase


class SubmitBusinessUseCase(BaseUseCase):
    def execute_core(self, command: ResourceCommand, resource: Any) -> Any:
        pass

    def build_response(self, command: ResourceCommand, resource: Any, core_result: Any,
                       events: list[dict[str, Any]]) -> ActionResult:
        pass

    def load_resource(self, command: ResourceCommand) -> Any:
        pass

    def run(self, command):
        return ActionResult(
            ok=True,
            code="OK",
            message="业务提交成功",
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
                "task": True,
            },
            refresh={
                "workspace": True,
                "todos": True,
            },
        )
