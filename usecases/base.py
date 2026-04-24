# metora/usecases/base.py

from core.context import MetoraContext


class BaseUseCase:
    def __init__(self, metora: MetoraContext):
        self.metora = metora

    @property
    def engine(self):
        return self.metora.engine

    def run(self, command):
        return self.execute(command)

    def execute(self, command):
        raise NotImplementedError
