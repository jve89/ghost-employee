from abc import ABC, abstractmethod
from app.core.models import Summary, Task, ExportResult, JobConfig

class Summariser(ABC):
    @abstractmethod
    def summarise(self, text: str, source_file: str) -> Summary:
        pass

class TaskParser(ABC):
    @abstractmethod
    def extract_tasks(self, summary: Summary) -> list[Task]:
        pass

class Executor(ABC):
    @abstractmethod
    def execute(self, task: Task) -> bool:
        pass

class Exporter(ABC):
    @abstractmethod
    def export(self, task: Task) -> ExportResult:
        pass

class Job(ABC):
    @abstractmethod
    def run(self, config: JobConfig):
        pass
