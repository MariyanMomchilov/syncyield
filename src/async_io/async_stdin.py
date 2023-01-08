from . import get_scheduler
from .readable import Readable
from .writable import Writable
from sys import stdin


class AsyncStdInWrapper(Readable[str], Writable[str]):

    def __init__(self) -> None:
        super().__init__()
        self._sched = get_scheduler()

    async def read(self, size=-1) -> str:
        self._sched.fd_monitor.watch_read(stdin.fileno(), self._sched.current)
        self._sched.current = None
        await self._sched.switch()
        return stdin.read(size)

    async def write(self, source: str) -> int:
        self._sched.fd_monitor.watch_write(stdin.fileno(), self._sched.current)
        self._sched.current = None
        await self._sched.switch()
        return stdin.write(source)
