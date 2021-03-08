import argparse
import asyncio
import logging
import random
from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock
from task_manager_service.task_manager_factory import TaskManagerFactory


async def scenario(behaviour: str, capacity: int, processes: dict):
    """ 1. Add custom number of processes with low, medium and high priorities
        2. List processes in order based on priority, id and time
        3. Kill a single process with randomly chosen pid
        4. List processes in order based on priority, id and time
        5. Kill group of group with randomly chosen priority
        6. List processes in order based on priority, id and time
        7. Kill all remaining processes
        8. List processes in order based on priority, id and time"""
    async with TaskManagerFactory.get_task_manager(behaviour, capacity) as t:
        pids = list()
        for key, value in processes.items():
            for i in range(value):
                process = ProcessMock(key)
                pid = await t.add(process)
                if pid is not None:
                    pids.append(pid)
        pid_to_kill = pids[random.randint(0, len(pids) - 1)]
        l = await t.list('priority')
        logger.info(f"Priority-based list with length {len(l)}: {l}")
        l = await t.list('id')
        logger.info(f"Id-based list with length {len(l)}: {l}")
        l = await t.list('time')
        logger.info(f"Time-based list with length {len(l)}: {l}")

        await t.kill(pid_to_kill)

        l = await t.list('priority')
        logger.info(f"Priority-based list with length {len(l)}: {l}")
        l = await t.list('id')
        logger.info(f"Id-based list with length {len(l)}: {l}")
        l = await t.list('time')
        logger.info(f"Time-based list with length {len(l)}: {l}")

        await t.kill_group(random.randint(0, 2))

        l = await t.list('priority')
        logger.info(f"Priority-based list with length {len(l)}: {l}")
        l = await t.list('id')
        logger.info(f"Id-based list with length {len(l)}: {l}")
        l = await t.list('time')
        logger.info(f"Time-based list with length {len(l)}: {l}")


def main(behaviour: str, capacity: int, processes: dict):
    logger.setLevel(logging.INFO)
    logger.info(f"Task Manager service starting...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scenario(behaviour, capacity, processes))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Choose Task Manager behaviour')
    parser.add_argument('--behaviour',
                        type=str,
                        default='fifo',
                        choices=['default', 'fifo', 'priority_based'],
                        help='behaviour of task manager, one of [default, fifo, priority_based]')
    parser.add_argument('--capacity',
                        type=int,
                        default=10,
                        help='capacity of task manager')
    parser.add_argument('--low_processes_count',
                        type=int,
                        default=8,
                        help='number of low priority processes to create')
    parser.add_argument('--medium_processes_count',
                        type=int,
                        default=3,
                        help='number of medium priority processes to create')
    parser.add_argument('--high_processes_count',
                        type=int,
                        default=5,
                        help='number of high priority processes to create')
    args = parser.parse_args()
    processes = {0: args.high_processes_count, 1: args.medium_processes_count, 2: args.low_processes_count}
    main(args.behaviour, args.capacity, processes)
