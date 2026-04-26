from packages.metora.engines.base import BaseEngine


class WorkflowEngine(BaseEngine):
    engine_name = "workflow"

    def start(self, *, business_id, workflow_code, values=None):
        pass

    def get_workflow(self, workflow_id):
        pass

    def get_workflow_by_business(self, business_id):
        pass

    def resolve_next_node(self, *, workflow_id, current_node_id, values=None):
        pass

    def move_to_node(self, *, workflow_id, node_id):
        pass

    def complete(self, *, workflow_id):
        pass

    def reject(self, *, workflow_id):
        pass

    def return_back(self, *, workflow_id):
        pass