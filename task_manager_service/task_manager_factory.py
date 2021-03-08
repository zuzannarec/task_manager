from task_manager_service.task_manager_default import TaskManagerDefault
from task_manager_service.task_manager_fifo import TaskManagerFifo
from task_manager_service.task_manager_priority_based import TaskManagerPriorityBased


class TaskManagerFactory:
    @staticmethod
    def get_task_manager(behaviour: str, capacity: int):
        if behaviour == 'default':
            return TaskManagerDefault(capacity)
        if behaviour == 'fifo':
            return TaskManagerFifo(capacity)
        if behaviour == 'priority_based':
            return TaskManagerPriorityBased(capacity)
