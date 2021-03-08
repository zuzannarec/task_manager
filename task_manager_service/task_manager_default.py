import asyncio
import uuid

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock
from task_manager_service.task_manager import ITaskManager


class TaskManagerDefault(ITaskManager):
    def __init__(self, capacity: int):
        if capacity < 1:
            logger.error(f"Incorrect capacity value: {capacity}. Setting capacity to 1")
            capacity = 1
        self.capacity = capacity
        self.processes_lock = asyncio.Lock()
        self.running_lock = asyncio.Lock()
        self.running = asyncio.Event()
        self.processed_lock = asyncio.Lock()
        self.processed = asyncio.Event()
        self.finished = asyncio.Queue()
        self.processes = dict()  # dict of ProcessMock objects, pid: ProcessMock

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.monitor_finished_tasks())
        await self.running.wait()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logger.info("Closing Task Manager. Killing all...")
        await self.kill_all()
        async with self.running_lock:
            self.running.clear()

    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
        async with self.processes_lock:
            if len(self.processes) < self.capacity:
                pid = await process.run(self.finished)
                self.processes[pid] = process
                logger.info(f"Created process with pid: {pid}, priority: {process.priority}")
                return pid
        logger.warning(f"Cannot create a new process. The maximum capacity {self.capacity} has been reached")
        return None

    async def list(self, order: str) -> list:
        if order == 'priority':
            async with self.processes_lock:
                return sorted(self.processes.values(), key=lambda x: x.priority)
        if order == 'time':
            async with self.processes_lock:
                return sorted(self.processes.values(), key=lambda x: x.timestamp)
        if order == 'id':
            async with self.processes_lock:
                return sorted(self.processes.values(), key=lambda x: x.pid)

    async def kill(self, pid: uuid.uuid1):
        async with self.processes_lock:
            if pid not in self.processes.keys():
                logger.warning(f"Cannot kill process. No such pid: {pid}")
                return
            process = self.processes[pid]
            priority = process.priority
            process.kill()
            del self.processes[pid]
        logger.info(f"Killed process with pid: {pid}, priority: {priority}")

    async def kill_group(self, priority: str):
        pids = list()
        async with self.processes_lock:
            for pid, process in self.processes.items():
                if process.priority == priority:
                    process.kill()
                    pids.append(pid)
            for pid in pids:
                del self.processes[pid]
        logger.info(f"All ({len(pids)}) processes with priority {priority} killed")

    async def kill_all(self):
        async with self.processes_lock:
            for pid, process in self.processes.items():
                process.kill()
            self.processes = dict()
        logger.info(f"All processes killed")

    async def clean_up_(self, pid: uuid.uuid1()):
        async with self.processes_lock:
            logger.info(f"Clean up finished process with pid: {pid}")
            del self.processes[pid]

    async def monitor_finished_tasks(self):
        logger.info("Starting monitoring finished tasks...")
        async with self.running_lock:
            self.running.set()
        while True:
            async with self.running_lock:
                if not self.running.is_set():
                    return
            try:
                pid = await asyncio.wait_for(self.finished.get(), timeout=1)
                await self.clean_up_(pid)
            except:
                pass
