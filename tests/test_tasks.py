from src.core import get_scheduler, Task, CancelledTask

sched = get_scheduler()


async def fib(n: int):
    if n == 0 or n == 1:
        return 1
    a = 1
    b = 1
    i = 1
    while i < n:
        c = a + b
        a = b
        b = c
        await sched.switch()
        i += 1
    return b


def test_task_cancelation():
    task = Task(fib(5))
    task.cancel()
    try:
        task.start()
    except CancelledTask as e:
        pass
    sched.run()


def test_task_result_exception():
    task = Task(fib(5))
    task.cancel()
    try:
        task.result
    except CancelledTask as e:
        pass
    sched.run()
    assert task.done


def test_task_result():
    task = Task(fib(5))
    task.start()
    sched.run()
    assert task.result == 8
