"""progress task pool

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import List, Optional

from .console import CONSOLE, Console
from .progress import Progress
from .task_pool import Task, TaskPool


class ProgressTask(Task):

    def __init__(self, name: str, total: int = 1, units: str = '', start: bool = True):
        self.progress: Optional[Progress] = None
        self.total: int = total
        self.units: str = units
        self.start: bool = start
        super().__init__(name)

    def before_task(self) -> None:
        super().before_task()
        self.progress.add_subtask(self.name, total=self.total, units=self.units, start=self.start)

    def after_task(self) -> None:
        super().after_task()
        if not self.cancelled:
            self.progress.complete_subtask(self.name)


class ProgressTaskPool(TaskPool):

    def __init__(self, jobs: int, title: str, units: str = '',
                 console: Console = CONSOLE.stdout_console):
        self._title: str = title
        self._units = units
        self.progress: Progress = Progress(console=console)
        super().__init__(jobs)

    def __enter__(self):
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.progress.stop()

    def before_tasks(self, tasks: List[ProgressTask]) -> None:
        super().before_tasks(tasks)
        for task in tasks:
            task.progress = self.progress
        self.progress.start()
        self.progress.add_task(self._title, total=len(tasks), units=self._units)

    def after_tasks(self, tasks: List[ProgressTask]) -> None:
        super().after_tasks(tasks)
        if not self.cancelled:
            self.progress.complete_task(self._title)
        self.progress.stop(clear_lines=not self.cancelled)

    def after_task(self, task: ProgressTask) -> None:
        super().after_task(task)
        if not self.cancelled:
            self.progress.update_task(self._title, advance=1)
