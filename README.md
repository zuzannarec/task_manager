# task_manager
>Build Docker image (workdir task_manager):

```
docker build . --tag task_manager:01
```

> The application runs the following test scenario:
>
1. Add custom number of processes with low, medium and high priorities
2. List processes in order based on priority, id and time
3. Set a single, randomly chosen process completed
4. List processes in order based on priority, id and time
5. Kill a single process with randomly chosen pid
6. List processes in order based on priority, id and time
7. Kill group of group with randomly chosen priority
8. List processes in order based on priority, id and time
9. Kill all remaining processes
10. List processes in order based on priority, id and time

> Default parameters:
>
1. behaviour = 'default'
2. capacity = 10
3. low_processes_count = 15
4. medium_processes_count = 7
5. high_processes_count = 10

>Run with default parameters:

```
docker run task_manager:01
```

>Display help:

```
docker run task_manager:01 --help
```

>Run with custom parameters:

```
docker run task_manager:01 --behaviour 'fifo' --capacity 1 --low_processes_count 3 --medium_processes_count 10 --high_processes_count 1
```

>TODO

add unit tests, add component tests