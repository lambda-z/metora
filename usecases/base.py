
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.commands import ResourceCommand
from core.results import ActionResult


class BaseUseCase(ABC):
    use_transaction: bool = False

    def run(self, command: ResourceCommand) -> ActionResult:
        resource = self.load_resource(command)

        auth_result = self.authorize(command, resource)
        if auth_result is not None:
            return auth_result

        validate_result = self.validate(command, resource)
        if validate_result is not None:
            return validate_result

        self.before_execute(command, resource)

        core_result = self.execute_core(command, resource)

        self.after_execute(command, resource, core_result)

        events = self.emit_events(command, resource, core_result)

        self.audit(command, resource, core_result)

        return self.build_response(command, resource, core_result, events)

    @abstractmethod
    def load_resource(self, command: ResourceCommand) -> Any:
        raise NotImplementedError

    def authorize(self, command: ResourceCommand, resource: Any) -> ActionResult | None:
        return None

    def validate(self, command: ResourceCommand, resource: Any) -> ActionResult | None:
        return None

    def before_execute(self, command: ResourceCommand, resource: Any) -> None:
        pass

    @abstractmethod
    def execute_core(self, command: ResourceCommand, resource: Any) -> Any:
        raise NotImplementedError

    def after_execute(self, command: ResourceCommand, resource: Any, core_result: Any) -> None:
        pass

    def emit_events(
        self,
        command: ResourceCommand,
        resource: Any,
        core_result: Any,
    ) -> list[dict[str, Any]]:
        return []

    def audit(self, command: ResourceCommand, resource: Any, core_result: Any) -> None:
        pass

    @abstractmethod
    def build_response(
        self,
        command: ResourceCommand,
        resource: Any,
        core_result: Any,
        events: list[dict[str, Any]],
    ) -> ActionResult:
        raise NotImplementedError