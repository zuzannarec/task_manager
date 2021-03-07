from task_manager_service.Process import Process
from task_manager_service.task_manager import TaskManager


class TaskManagerFifo(TaskManager):
    def __init__(self):
        self.processes = list()

    async def add(self, process: Process) -> str:
        pass

    async def list(self, order: str) -> list:
        pass

    async def kill(self, pid: str):
        pass

    async def kill_group(self, priority: str):
        pass

    async def kill_all(self):
        pass
