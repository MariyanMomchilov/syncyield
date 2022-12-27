from types import coroutine
from src.core.scheduler import Scheduler


count_container = []


def close_counter_handler(counter: int):
    def close_sched(sched: Scheduler):
        nonlocal counter
        counter -= 1
        if counter == 0:
            sched.close()
    return close_sched


signal_close = close_counter_handler(2)


@coroutine
def _countup(to: int, sched: Scheduler):
    i = 0
    while i < to:
        count_container.append(i)
        yield i
        i += 1
    signal_close(sched)


@coroutine
def _countdown(to: int, sched: Scheduler):
    i = to - 1
    while i >= 0:
        count_container.append(i)
        yield i
        i -= 1
    signal_close(sched)


def test_scheduler_only_call_soon():
    sched = Scheduler()
    sched.call_soon(_countup(5, sched))
    sched.call_soon(_countdown(5, sched))
    sched.run()
    assert count_container == [0, 4, 1, 3, 2, 2, 3, 1, 4, 0]
