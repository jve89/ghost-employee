# app/plugins/__init__.py

from abc import ABC, abstractmethod
from app.core.models import Task

class Plugin(ABC):
    @abstractmethod
    def match(self, task: Task) -> bool:
        """Return True if this plugin can handle the given task."""
        pass

    @abstractmethod
    def run(self, task: Task) -> str:
        """Perform the task. Return a status message."""
        pass
