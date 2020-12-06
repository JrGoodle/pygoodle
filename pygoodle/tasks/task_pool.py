"""task pool

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from threading import Lock
from typing import Any, List, Optional

import trio

from pygoodle.console import disable_output


class Task(object):

    def __init__(self, name: str):
        self.name: str = name
        self._pool: Optional[TaskPool] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._pool = None
        pass

    @property
    def cancelled(self) -> bool:
        return self._pool.cancelled

    def in_pool(self, pool: 'TaskPool') -> 'Task':
        self._pool = pool
        return self

    def before_task(self) -> None:
        pass

    def after_task(self) -> None:
        pass

    def run(self) -> None:
        pass


class TaskPool(object):

    def __init__(self, jobs: int):
        self._jobs: int = jobs
        self._lock: Lock = Lock()
        self._results: Optional[List[Any]] = None
        self.cancelled: bool = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def before_tasks(self, tasks: List[Task]) -> None:
        pass

    def before_task(self, task: Task) -> None:
        pass

    def after_task(self, task: Task) -> None:
        pass

    def after_tasks(self, tasks: List[Task]) -> None:
        pass

    @disable_output
    def run(self, tasks: List[Task]) -> List[Any]:
        return trio.run(self._run, tasks)

    async def _run(self, tasks: List[Task]) -> List[Any]:
        try:
            async with trio.open_nursery() as nursery:
                limit = trio.CapacityLimiter(self._jobs)
                self.before_tasks(tasks)
                self._results = []
                try:
                    for task in tasks:
                        await limit.acquire_on_behalf_of(task.name)
                        nursery.start_soon(self._run_task, task, limit, nursery)
                except BaseException:
                    nursery.cancel_scope.cancel()
                    self.cancelled = True
                    raise
            return self._results
        except BaseException:
            self.cancelled = True
            raise
        finally:
            self.after_tasks(tasks)

    async def _run_task(self, task: Task, limit: trio.CapacityLimiter, nursery: trio.Nursery) -> Any:
        with task.in_pool(self):
            try:
                self.before_task(task)
                task.before_task()
                result = await trio.to_thread.run_sync(task.run)
                with self._lock:
                    self._results.append(result)
            except BaseException:
                self.cancelled = True
                nursery.cancel_scope.cancel()
                raise
            finally:
                task.after_task()
                self.after_task(task)
                limit.release_on_behalf_of(task.name)