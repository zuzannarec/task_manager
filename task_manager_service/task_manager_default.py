import asyncio
import uuid

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock
from task_manager_service.task_manager import ITaskManager


class TaskManagerDefault(ITaskManager):
    def __init__(self, capacity: int):
        self.processes_lock = asyncio.Lock()
        self.running_lock = asyncio.Lock()
        self.running = asyncio.Event()
        self.processed_lock = asyncio.Lock()
        self.processed = asyncio.Event()
        self.capacity = capacity
        self.finished = asyncio.Queue()
        self.processes = dict()  # dict of ProcessMock objects, pid: ProcessMock

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.finished_worker())
        await self.running.wait()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.kill_all()
        async with self.running_lock:
            self.running.clear()

    async def add(self, process: ProcessMock) -> (uuid.uuid1, None):
        async with self.processes_lock:
            if len(self.processes) < self.capacity:
                pid = process.run(self.finished)
                priority = process.priority
                self.processes[pid] = process
                logger.info(f"Created process with pid: {pid}, priority: {priority}")
                return pid
        logger.error(f"Cannot create a new process. The maximum capacity {self.capacity} has been reached")
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

    async def kill(self, pid: str):
        async with self.processes_lock:
            process = self.processes[pid]
        priority = process.priority
        await process.kill()
        logger.info(f"Killed process with pid: {pid}, priority: {priority}")

    async def kill_group(self, priority: str):
        async with self.processes_lock:
            for _, process in self.processes.items():
                if process.priority == priority:
                    await process.kill()
        logger.info(f"All processes with priority {priority} killed")

    async def kill_all(self):
        async with self.processes_lock:
            for _, process in self.processes.items():
                await process.kill()
        logger.info(f"All processes killed")

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
                    del self.processes[pid]
            except:
                pass
