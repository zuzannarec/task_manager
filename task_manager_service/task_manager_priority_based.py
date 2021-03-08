import uuid

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock, Priority
from task_manager_service.task_manager_default import TaskManagerDefault


class TaskManagerPriorityBased(TaskManagerDefault):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.priority_to_pid = {Priority.HIGH: list(), Priority.MEDIUM: list(),
                                Priority.LOW: list()}  # priority to list of pids

    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
        pid_to_remove = None
        logger.info(f"Add process with priority: {process.priority}...")
        async with self.processes_lock:
            if len(self.processes) >= self.capacity:
                pid_to_remove = self.get_lower_priority_pid_(process.priority)
                if pid_to_remove is None:
                    logger.warning(
                        "Cannot create a new process. The maximum capacity has been reached and nothing to remove")
                    return
                priority_to_remove = self.processes[pid_to_remove].priority
        if pid_to_remove is not None:
            logger.warning(
                f"The maximum capacity {self.capacity} has been reached. "
                f"Removing process with pid {pid_to_remove}, priority: {priority_to_remove}")
            await self.kill(pid_to_remove)
        pid = await process.run(self.finished)
        async with self.processes_lock:
            self.priority_to_pid[process.priority].append(pid)
            self.processes[pid] = process
        logger.info(f"Created process with pid: {pid}, priority: {process.priority}")
        return pid

    def get_lower_priority_pid_(self, new_process_priority: Priority) -> uuid.uuid1:
        priorities_sorted = sorted(self.priority_to_pid.keys(), reverse=True)
        for priority in priorities_sorted:
            if priority <= new_process_priority:
                return None
            if len(self.priority_to_pid[priority]):
                # return pid of process to remove and remove if from self.priority_to_pid data structure
                return self.priority_to_pid[priority].pop(0)

    async def clean_up_(self, pid: uuid.uuid1()):
        async with self.processes_lock:
            logger.info(f"Clean up finished process with pid: {pid}")
            priority = self.processes[pid].priority
            del self.processes[pid]
            self.priority_to_pid[priority].remove(pid)
