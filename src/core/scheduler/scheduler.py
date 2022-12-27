"""Scheduler module."""

from typing import Coroutine
import heapq
from collections import deque


class Scheduler:
    """Scheduler class. Manages scheduling and execution of coroutines."""

    def __init__(self) -> None:
        """Init."""
        self._pending: deque[Coroutine] = deque()
        self._sleeping: list[Coroutine] = []
        self._current_coro: Coroutine | None = None
        self._closed = False

    def closed(self):
        return self._closed

    def close(self):
        self._closed = True

    def call_soon(self, coro: Coroutine):
        """Schedules coroutine for execution."""
        self._pending.append(coro)

    def run(self) -> None:
        """Run the scheduler."""
        while not self._closed:
            if not self._pending:
                continue
            try:
                self._current_coro = self._pending.popleft()
                self._current_coro.send(None)
                if self._current_coro is not None:
                    self.call_soon(self._current_coro)
            except StopIteration:
                pass
            except Exception:
                raise
