import uuid

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock
from task_manager_service.task_manager_default import TaskManagerDefault


class TaskManagerFifo(TaskManagerDefault):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.pids = list()  # list of pids in order of creation

    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
        pid_to_remove = None
        async with self.processes_lock:
            if len(self.pids) >= self.capacity:
                pid_to_remove = self.pids.pop()  # remove pid of the oldest process
        if pid_to_remove:
            logger.warning(
                f"The maximum capacity {self.capacity} has been reached. Removing process with pid {pid_to_remove}")
            await self.kill(pid_to_remove)  # kill the oldest process
        pid = await process.run(self.finished)
        async with self.processes_lock:
            self.pids.append(pid)
            self.processes[pid] = process
        logger.info(f"Created process with pid: {pid}, priority: {process.priority}")
        return pid

    async def clean_up_(self, pid: uuid.uuid1()):
        async with self.processes_lock:
            logger.info(f"Clean up finished process with pid: {pid}")
            del self.processes[pid]
            self.pids.remove(pid)
