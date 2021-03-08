import asyncio
import uuid

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock
from task_manager_service.task_manager_default import TaskManagerDefault


class TaskManagerPriorityBased(TaskManagerDefault):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.priority_to_pid = {0: list(), 1: list(), 2: list()}  # priority to list of pids

    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
        async with self.processes_lock:
            if len(self.processes) >= self.capacity:
                if process.priority == 0 and len(self.priority_to_pid[2]):
                    removed = self.priority_to_pid[2].pop(0).pid
                elif process.priority == 0 and len(self.priority_to_pid[1]):
                    removed = self.priority_to_pid[1].pop(0).pid
                elif process.priority == 1 and len(self.priority_to_pid[2]):
                    removed = self.priority_to_pid[2].pop(0).pid
                else:
                    logger.error("Cannot create a new process. The maximum capacity has been reached")
                    return None
                logger.warning(
                    f"The maximum capacity {self.capacity} has been reached. Process with pid {removed} removed")
                await self.kill(removed)
            pid = process.run(self.finished)
            priority = process.priority
            self.priority_to_pid[priority].append(pid)
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
                    priority = self.processes[pid].priority
                    for idx, value in enumerate(self.priority_to_pid[priority]):
                        if value == pid:
                            self.priority_to_pid.pop(idx)
                    del self.processes[pid]
            except:
                pass
