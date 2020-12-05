"""pygoodle ftp utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Any, List, Optional

from pygoodle.util.console import CONSOLE, Console
from pygoodle.util.progress import Progress
from pygoodle.util.task_pool import Task, TaskPool


class ProgressTask(Task):

    def __init__(self, name: str, total: int = 1, units: str = '', start: bool = True):
        self.progress: Optional[Progress] = None
        self.total: int = total
        self.units: str = units
        self.start: bool = start
        super().__init__(name)

    def before_task(self) -> None:
        self.progress.add_subtask(self.name, total=self.total, units=self.units, start=self.start)

    def after_task(self) -> None:
        self.progress.complete_subtask(self.name)

    def run(self) -> Any:
        pass


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
        for task in tasks:
            task.progress = self.progress
        self.progress.start()
        self.progress.add_task(self._title, total=len(tasks), units=self._units)

    def after_tasks(self, tasks: List[ProgressTask]) -> None:
        self.progress.complete_task(self._title)
        self.progress.stop()

    def after_task(self, task: ProgressTask) -> None:
        self.progress.update_task(self._title, advance=1)
