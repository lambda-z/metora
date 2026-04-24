# metora/usecases/base.py
from core.commands import ResourceCommand
from core.context import MetoraContext
from core.results import ActionResult


class BaseUseCase:
    def __init__(self, metora: MetoraContext):
        self.metora = metora

    @property
    def engine(self):
        return self.metora.engine

    def run(self, command: ResourceCommand):
        return self.execute(command)

    def execute(self, command: ResourceCommand) -> ActionResult:
        raise NotImplementedError
