from typing import Coroutine
from .scheduler import get_scheduler


class TaskNotDoneError(Exception):
    pass


class CancelledTask(Exception):
    pass


class Task:
    """Coroutine wrapper, represent a future result of executing the coroutine."""

    def __init__(self, coro: Coroutine) -> None:
        self.coro = coro
        self._result = None
        self._exception = None
        self._done = False
        self._cb_sent = None
        self._canceled = False

    @property
    def done(self):
        return self._done

    @property
    def canceled(self):
        return self._canceled

    def cancel(self):
        """Cancel the execution of Task."""
        if not self.done:
            sched = get_scheduler()
            sched.remove_from_scheduler(self.coro)
            self.coro.close()
            self._canceled = True
            self._done = True

    def start(self):
        """Schedules the Task for execution and updates the result value."""
        sched = get_scheduler()
        self._cb_sent = self._call_soon_cb()
        sched.call_soon(self._cb_sent)

    async def _call_soon_cb(self):
        try:
            result = await self.coro()
            self._result = result
        except Exception as e:
            self._exception = e

    @property
    def result(self):
        """Return result if the task is done or raise TaskNotDoneError."""
        if not self.done:
            raise TaskNotDoneError()
        if self.canceled:
            raise CancelledTask()
        if self._exception is not None:
            raise self._exception
        return self._result

    @staticmethod
    async def map(tasks: list['Task']):
        sched = get_scheduler()

        for task in tasks:
            task.start()

        while any(not task.done for task in tasks):
            await sched.switch()

        return map(lambda t: t.result, tasks)
