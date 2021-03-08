import argparse
import asyncio
import logging
import random

from task_manager_service.logger import logger
from task_manager_service.process_mock import ProcessMock, Priority
from task_manager_service.task_manager_factory import TaskManagerFactory


async def list_all(t):
    listed = await t.list('priority')
    logger.info(f"Priority-based list with length {len(listed)}: {listed}")
    listed = await t.list('id')
    logger.info(f"Id-based list with length {len(listed)}: {listed}")
    listed = await t.list('time')
    logger.info(f"Time-based list with length {len(listed)}: {listed}")


async def scenario(behaviour: str, capacity: int, processes_to_create: dict):
    """ 1. Add custom number of processes with low, medium and high priorities
        2. List processes in order based on priority, id and time
        3. Set a single, randomly chosen process completed
        4. List processes in order based on priority, id and time
        5. Kill a single process with randomly chosen pid
        6. List processes in order based on priority, id and time
        7. Kill group of group with randomly chosen priority
        8. List processes in order based on priority, id and time
        9. Kill all remaining processes
        10. List processes in order based on priority, id and time"""
    async with TaskManagerFactory.get_task_manager(behaviour, capacity) as t:
        # 1. Add custom number of processes with low, medium and high priorities
        all_processes = list()
        pids = list()
        processes = list()
        for priority, processes_list in processes_to_create.items():
            for i in range(processes_list):
                process = ProcessMock(priority)
                all_processes.append(process)
        random.shuffle(all_processes)  # shuffle to run processes with different priorities in random order
        for process in all_processes:
                pid = await t.add(process)
                if pid is None:
                    continue
                pids.append(pid)
                processes.append(process)
        # choose random pid to kill from first half of list
        pid_to_kill = pids[random.randint(0, (len(pids) - 1) // 2)]
        # choose random process to set completed from second half of list
        process_to_complete = processes[random.randint((len(pids) - 1) // 2 + 1, len(pids) - 1)]

        # 2. List processes in order based on priority, id and time
        await list_all(t)

        # 3. Set a single, randomly chosen process completed
        await process_to_complete.set_completed()

        # 4. List processes in order based on priority, id and time
        await list_all(t)

        # 5. Kill a single process with randomly chosen pid
        await t.kill(pid_to_kill)

        # 6. List processes in order based on priority, id and time
        await list_all(t)

        # 7. Kill group of group with randomly chosen priority
        await t.kill_group(random.randint(Priority.HIGH, Priority.LOW))

        # 8. List processes in order based on priority, id and time
        await list_all(t)

        # 9. Kill all remaining processes
        await t.kill_all()

        # 10. List processes in order based on priority, id and time
        await list_all(t)


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
                        metavar='',
                        default='default',
                        choices=['default', 'fifo', 'priority_based'],
                        help='behaviour of task manager, one of [default, fifo, priority_based]')
    parser.add_argument('--capacity',
                        type=int,
                        metavar='',
                        default=10,
                        help='capacity of task manager')
    parser.add_argument('--low_processes_count',
                        dest='low_processes_count',
                        type=int,
                        metavar='',
                        default=15,
                        help='number of low priority processes to create')
    parser.add_argument('--medium_processes_count',
                        type=int,
                        metavar='',
                        default=7,
                        help='number of medium priority processes to create')
    parser.add_argument('--high_processes_count',
                        type=int,
                        metavar='',
                        default=10,
                        help='number of high priority processes to create')
    args = parser.parse_args()
    processes = {Priority(0): args.high_processes_count,
                 Priority(1): args.medium_processes_count,
                 Priority(2): args.low_processes_count}
    main(args.behaviour, args.capacity, processes)
