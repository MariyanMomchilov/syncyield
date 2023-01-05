from io import TextIOWrapper, IOBase, BufferedReader, BufferedWriter
from . import get_scheduler
from .readable import Readable
from .writable import Writable


class AsyncTextIOWrapper(Readable[str], Writable[str]):
    """Async wrapper for IOBase class. This is a simple example of how to use the scheduler for nonblocking I/O"""
    def __init__(self, f: TextIOWrapper | IOBase | BufferedReader | BufferedWriter) -> None:
        super().__init__()
        self.f = f
        self._sched = get_scheduler()

    async def read(self, size: int = -1) -> str:
        "Async read"
        self._sched.fd_monitor.watch_read(self.f.fileno(), self._sched.current)
        self._sched._current_coro = None
        await self._sched.switch()
        return self.f.read(size)

    async def write(self, source: str) -> int:
        "Async write"
        self._sched.fd_monitor.watch_write(self.f.fileno(), self._sched.current)
        self._sched._current_coro = None
        await self._sched.switch()
        return self.f.write(source)
