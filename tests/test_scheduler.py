from types import coroutine
from collections import deque

from src.core.scheduler import Scheduler


count_container = []


def close_counter_handler(counter: int):
    def close_sched(sched: Scheduler):
        nonlocal counter
        counter -= 1
        if counter == 0:
            sched.close()
    return close_sched


@coroutine
def _countup(to: int, sched: Scheduler, handler):
    i = 0
    while i < to:
        count_container.append(i)
        yield i
        i += 1
    handler(sched)


@coroutine
def _countdown(to: int, sched: Scheduler, handler):
    i = to - 1
    while i >= 0:
        count_container.append(i)
        yield i
        i -= 1
    handler(sched)


def test_scheduler_only_call_soon():
    global count_container
    count_container = []
    signal_close = close_counter_handler(2)
    sched = Scheduler()
    sched.call_soon(_countup(5, sched, signal_close))
    sched.call_soon(_countdown(5, sched, signal_close))
    sched.run()
    assert count_container == [0, 4, 1, 3, 2, 2, 3, 1, 4, 0]


def test_scheduler_call_later():
    global count_container
    count_container = []
    sched = Scheduler()
    signal_close = close_counter_handler(2)
    sched.call_later(_countup(5, sched, signal_close), 1)
    sched.call_soon(_countdown(5, sched, signal_close))
    sched.run()
    assert count_container == [4, 3, 2, 1, 0, 0, 1, 2, 3, 4]


class TestException(Exception):
    pass


async def throw_exception():
    raise TestException()


def test_sched_exception_handling():
    sched = Scheduler()
    sched.call_soon(throw_exception())
    try:
        sched.run()
    except TestException:
        assert True
        return
    assert False


logs = []
sched = Scheduler()


async def stop_scheduler():
    while sched._pending or sched._sleeping:
        await sched.switch()
    sched.close()


async def log_twice(string: str):
    logs.append(string + '(1)')
    await sched.switch()
    logs.append(string + '(2)')


def test_sched_switch():
    sched.call_soon(log_twice('First'))
    sched.call_soon(log_twice('Second'))
    sched.call_soon(stop_scheduler())
    sched.run()
    assert logs == ['First(1)', 'Second(1)', 'First(2)', 'Second(2)']


async def log_sleep_twice(string: str, sleep_time=1):
    logs.append(string + '(1)')
    await sched.sleep(sleep_time)
    logs.append(string + '(2)')


def test_sched_sleep():
    global logs
    logs = []
    global sched
    sched = Scheduler()
    sched._closed = False
    sched._pending = deque()
    sched._sleeping = []
    sched.call_soon(log_sleep_twice('First', 2))
    sched.call_soon(log_sleep_twice('Second', 1))
    sched.call_soon(stop_scheduler())
    sched.run()
    assert logs == ['First(1)', 'Second(1)', 'Second(2)', 'First(2)']
