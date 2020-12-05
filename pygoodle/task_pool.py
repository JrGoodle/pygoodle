"""pygoodle ftp utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from threading import Lock
from typing import Any, List, Optional

import trio

from .console import disable_output


class Task(object):

    def __init__(self, name: str):
        self.name: str = name

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def before_tasks(self, tasks: List[Task]) -> None:
        pass

    def after_tasks(self, tasks: List[Task]) -> None:
        pass

    def before_task(self, task: Task) -> None:
        pass

    def after_task(self, task: Task) -> None:
        pass

    @disable_output
    def run(self, tasks: List[Task]) -> List[Any]:
        return trio.run(self._run, tasks)

    async def _run(self, tasks: List[Task]) -> List[Any]:
        limit = trio.CapacityLimiter(self._jobs)
        self.before_tasks(tasks)
        self._results = []
        async with trio.open_nursery() as nursery:
            for task in tasks:
                await limit.acquire_on_behalf_of(task.name)
                nursery.start_soon(self._run_task, task, limit)
        self.after_tasks(tasks)
        return self._results

    async def _run_task(self, task: Task, limit: trio.CapacityLimiter) -> Any:
        self.before_task(task)
        task.before_task()
        result = await trio.to_thread.run_sync(task.run)
        with self._lock:
            self._results.append(result)
        task.after_task()
        self.after_task(task)
        limit.release_on_behalf_of(task.name)
