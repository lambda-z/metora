# metora/usecases/base.py

from __future__ import annotations

from typing import Any

from core.commands import ResourceCommand
from core.context import MetoraContext
from core.resources import Resource
from core.results import ActionResult


class BaseUseCase:
    """
    UseCase 基类。

    职责：
        1. 接收 ResourceCommand
        2. 解析主 Resource
        3. 执行具体业务动作
    """

    resolve_main_resource: bool = True

    def __init__(self, metora: MetoraContext):
        self.metora = metora

    @property
    def engine(self):
        return self.metora.engine

    def run(self, command: ResourceCommand) -> ActionResult:
        resource = None

        if self.resolve_main_resource:
            resource = self.resolve_resource(command)

        return self.execute(command, resource)

    def resolve_resource(self, command: ResourceCommand) -> Resource | None:
        """
        根据 command.resource_ref 解析主资源。

        注意：
            如果是创建动作，例如 business.create，
            resource_ref.id 可能是 "new"，这时不应该解析已有资源。
        """

        if command.resource_ref.id in [None, "new"]:
            return None

        return self.metora.resource.resolve(command.resource_ref)

    def execute(
        self,
        command: ResourceCommand,
        resource: Resource | None = None,
    ) -> ActionResult:
        raise NotImplementedError
