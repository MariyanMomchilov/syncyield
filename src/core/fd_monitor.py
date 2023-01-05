"""FileDescriptorMonitor module."""
from typing import Coroutine
from select import select


class FileDescriptorMonitor:
    """Monitoring support for file descriptors."""

    def __init__(self) -> None:
        self._readers: dict[int, Coroutine] = {}
        self._writers: dict[int, Coroutine] = {}

    def watch_read(self, fd: int, coro: Coroutine):
        self._readers[fd] = coro

    def watch_write(self, fd: int, coro: Coroutine):
        self._writers[fd] = coro

    def remove_read(self, fd: int):
        self._readers.pop(fd, None)

    def remove_write(self, fd: int):
        self._writers.pop(fd, None)

    def get_read_fd_coros(self, fd: int):
        return self._readers.get(fd)
    
    def get_write_fd_coros(self, fd: int):
        return self._writers.get(fd)

    def monitor(self) -> tuple[list[int], list[int]]:
        if len(self._readers) == 0 and len(self._writers) == 0:
            return [], []

        read_ready, write_ready, _ = select(self._readers.keys(), self._writers.keys(), [], 1)
        return read_ready, write_ready
