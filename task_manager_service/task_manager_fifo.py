import asyncio
import uuid

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock
from task_manager_service.task_manager_default import TaskManagerDefault


class TaskManagerFifo(TaskManagerDefault):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.processes_list = list()  # list of ProcessMock objects

    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
        pid_to_remove = None
        async with self.processes_lock:
            if len(self.processes_list) >= self.capacity:
                pid_to_remove = self.processes_list[0].pid
        if pid_to_remove:
            await self.kill(pid_to_remove)
            logger.warning(
                f"The maximum capacity {self.capacity} has been reached. Process with pid {pid_to_remove} removed")
        pid = process.run(self.finished)
        priority = process.priority
        async with self.processes_lock:
            self.processes_list.append(process)
            self.processes[pid] = process
        logger.info(f"Created process with pid: {pid}, priority: {priority}")
        return pid

    async def finished_worker(self):
        logger.info("Starting finished worker...")
        async with self.running_lock:
            self.running.set()
        while True:
            async with self.running_lock:
                if not self.running.is_set():
                    return
            try:
                pid = await asyncio.wait_for(self.finished.get(), timeout=1)
                async with self.processes_lock:
                    for idx, process in enumerate(self.processes_list):
                        if process.pid == pid:
                            self.processes_list.pop(idx)
                    del self.processes[pid]
            except:
                pass
