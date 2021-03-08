import asyncio
import datetime
import uuid
from asyncio import Queue
from enum import IntEnum

from task_manager_service.logger import logger


class Priority(IntEnum):
    LOW = 2
    MEDIUM = 1
    HIGH = 0


class ProcessMock:
    def __init__(self, priority: Priority):
        self.finish_event = asyncio.Event()
        self.waiting = asyncio.Event()
        self.priority = priority  # LOW - 2, MEDIUM - 1, HIGH - 0
        self.timestamp = None
        self.process = None
        self.pid = None
        self.finish = False

    def __repr__(self):
        return f"PID:{self.pid} PRIORITY:{self.priority} TIMESTAMP:{self.timestamp}"

    async def run(self, finished: Queue) -> uuid.uuid1:
        """Simulate process run: generate timestamp, pid and start waiting for process completion"""
        self.timestamp = datetime.datetime.now()
        self.pid = uuid.uuid1()
        loop = asyncio.get_event_loop()
        loop.create_task(self.wait(finished))
        await self.waiting.wait()
        return self.pid

    async def wait(self, finished: Queue):
        """Wait for process to complete"""
        self.waiting.set()
        await self.finish_event.wait()
        if self.finish:
            logger.info(f"Completed, pid: {self.pid}")
            await finished.put(self.pid)

    def kill(self):
        """Kill process and call event.set() to break waiting for process completion"""
        self.finish_event.set()

    async def set_completed(self):
        """Simulate completion of the process"""
        self.finish = True
        self.finish_event.set()
        await asyncio.sleep(0.1)
