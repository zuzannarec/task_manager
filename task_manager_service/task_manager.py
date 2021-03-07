import abc

from task_manager_service.Process import Process


class TaskManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def add(self, process: Process) -> str:
        pass

    @abc.abstractmethod
    async def list(self, order: str) -> list:
        pass

    @abc.abstractmethod
    async def kill(self, pid: str):
        pass

    @abc.abstractmethod
    async def kill_group(self, priority: str):
        pass

    @abc.abstractmethod
    async def kill_all(self):
        pass