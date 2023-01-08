"""FileDescriptorMonitor module."""
from typing import Coroutine
from select import select


class FileDescriptorMonitor:

    def __init__(self) -> None:
        """Init."""
        self._readers: dict[int, list[Coroutine]] = {}
        self._writers: dict[int, list[Coroutine]] = {}

    def watch_read(self, fd: int, coro: Coroutine):
        coros = self._readers.get(fd, [])
        coros.append(coro)
        self._readers[fd] = coros

    def watch_write(self, fd: int, coro: Coroutine):
        coros = self._writers.get(fd, [])
        coros.append(coro)
        self._writers[fd] = coros

    def remove_read(self, fd: int):
        self._readers.pop(fd, None)

    def remove_write(self, fd: int):
        self._writers.pop(fd, None)

    def get_read_fd_coro(self, fd: int):
        coro = self._readers.get(fd, []).pop(0)
        return coro

    def get_write_fd_coro(self, fd: int):
        coro = self._writers.get(fd, []).pop(0)
        return coro

    def monitor(self) -> tuple[list[int], list[int]]:
        if len(self._readers) == 0 and len(self._writers) == 0:
            return [], []

        read_ready, write_ready, _ = select(self._readers.keys(), self._writers.keys(), [], 1)
        return read_ready, write_ready
