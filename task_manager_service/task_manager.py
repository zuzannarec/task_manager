import abc
import uuid

from task_manager_service.process_mock import ProcessMock


class ITaskManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
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
