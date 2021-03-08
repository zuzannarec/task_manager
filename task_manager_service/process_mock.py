import asyncio
import datetime
import uuid
from asyncio import Queue


class ProcessMock:
    def __init__(self, priority: int):
        self.priority = priority  # low - 2, medium - 1, high - 0
        self.timestamp = None
        self.process = None
        self.event = asyncio.Event()
        self.pid = uuid.uuid1()

    def __repr__(self):
        return f"PID:{self.pid} PRIORITY:{self.priority} TIMESTAMP:{self.timestamp}"

    def run(self, finished: Queue) -> uuid.uuid1:
        self.timestamp = datetime.datetime.now()
        loop = asyncio.get_event_loop()
        loop.create_task(self.wait(finished))
        return self.pid

    async def wait(self, finished: Queue):
        await self.event.wait()
        await finished.put(self.pid)

    async def kill(self):
        self.event.set()
