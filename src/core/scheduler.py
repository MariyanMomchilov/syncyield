"""Scheduler module."""
from typing import Coroutine, Tuple
import heapq
from collections import deque
from time import time
from .fd_monitor import FileDescriptorMonitor


class Awaitable:
    """Awaitable object."""

    def __await__(self):
        yield


class Scheduler:
    """Scheduler class. Manages scheduling and execution of coroutines."""

    def __init__(self) -> None:
        self._pending: deque[Coroutine] = deque()
        self._sleeping: list[Tuple[float, int, Coroutine]] = []
        self._current_coro: Coroutine | None = None
        self._closed = False
        self._seq = 0
        self.fd_monitor = FileDescriptorMonitor()

    def _get_sleeping(self):
        if self._sleeping:
            deadline, _, coro = self._sleeping[0]
            if time() >= deadline:
                heapq.heappop(self._sleeping)
                return coro
        return None

    @property
    def current(self):
        """Get current running coroutine."""
        return self._current_coro

    @current.setter
    def current(self, coro: Coroutine | None):
        self._current_coro = coro

    @property
    def closed(self):
        """Check if scheduler is closed."""
        return self._closed

    @property
    def empty(self):
        return len(self._pending) == 0 and len(self._sleeping) == 0

    def close(self):
        """Close the scheduler for further execution and scheduling."""
        self._closed = True
        self._current_coro = None
        for coro in self._pending:
            coro.close()
        for _, _, coro in self._sleeping:
            coro.close()

    def call_soon(self, coro: Coroutine):
        """Schedules coroutine for execution."""
        self._pending.append(coro)

    def call_later(self, coro: Coroutine, seconds: int):
        """Schedules coroutine for execution after :seconds."""
        if seconds < 0:
            raise ValueError('seconds must be non negative')
        heapq.heappush(self._sleeping, (time() + seconds, self._seq, coro))
        self._seq += 1


    def remove_from_scheduler(self, coro: Coroutine):
        """Remove coroutine from scheduler."""
        if coro in self._pending:
            self._pending.remove(coro)
            return

        for fd, coro_lst in self.fd_monitor._readers.items():
            if coro in coro_lst:
                lst = coro_lst
                lst.remove(coro)
                self.fd_monitor._readers[fd] = lst
                return

        for fd, coro_lst in self.fd_monitor._writers.items():
            if coro in coro_lst:
                lst = coro_lst
                lst.remove(coro)
                self.fd_monitor._writers[fd] = lst
                return

        new_heap: list[tuple[float, int, Coroutine]] = []
        for t in self._sleeping:
            if t[2] is not coro:
                heapq.heappush(new_heap, t)
        self._sleeping = new_heap


    def run(self) -> None:
        """Run the scheduler."""
        while not self._closed and not self.empty:
            read_ready, write_ready = self.fd_monitor.monitor()
            for ready in read_ready:
                self._pending.append(self.fd_monitor.get_read_fd_coro(ready))
            for ready in write_ready:
                self._pending.append(self.fd_monitor.get_write_fd_coro(ready))
            coro = self._get_sleeping()
            if coro is not None:
                self._pending.append(coro)
            if not self._pending:
                continue
            try:
                self._current_coro = self._pending.popleft()
                self._current_coro.send(None)
                if self._current_coro is not None:
                    self.call_soon(self._current_coro)
                    self._current_coro = None
            except StopIteration:
                pass
            except Exception:
                raise

    async def switch(self):
        """Suspend current execution of coroutine."""
        await Awaitable()

    async def sleep(self, seconds: int = 0):
        """Suspend current execution of coroutine for :seconds."""
        if seconds < 0:
            raise ValueError('seconds must be non negative')

        self.call_later(self._current_coro, seconds)  # type: ignore
        self._current_coro = None
        await self.switch()


_scheduler = Scheduler()


def get_scheduler():
    return _scheduler


def set_scheduler(scheduler: Scheduler):
    global _scheduler
    _scheduler = scheduler
