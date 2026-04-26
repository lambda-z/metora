from packages.metora.engines.base import BaseEngine


class TaskEngine(BaseEngine):
    engine_name = "task"

    def create_task(self, *, business_id, workflow_id, node_id, node_name, assignee_id):
        pass

    def get_task(self, task_id):
        pass

    def complete_task(self, *, task_id, actor_id, action, comment=None):
        pass

    def approve_task(self, *, task_id, actor_id, comment=None):
        pass

    def reject_task(self, *, task_id, actor_id, comment=None):
        pass

    def return_task(self, *, task_id, actor_id, comment=None):
        pass

    def transfer_task(self, *, task_id, from_actor_id, to_actor_id, comment=None):
        pass

    def get_todos(self, *, actor_id, limit=20, offset=0):
        pass

    def get_done_tasks(self, *, actor_id, limit=20, offset=0):
        pass
