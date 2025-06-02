from app.core.models import JobConfig, Task
from app.core.interfaces import Job
from app.services.summary_service import SummaryService
from app.services.task_service import TaskService
from app.services.export_service import ExportService
from infrastructure.logger.job_status import job_status

class PrepareInternsJob(Job):
    def run(self, config: JobConfig):
        job_status.update(config.job_name)

        # 1. Define mock task inputs
        tasks = [
            Task(description="Prepare intern onboarding documents"),
            Task(description="Schedule intro calls with interns"),
        ]

        # 2. Summarise them
        summary_service = SummaryService(config)
        summaries = summary_service.generate_summaries(tasks)

        # 3. Extract refined tasks from summaries
        task_service = TaskService(config)
        refined_tasks = task_service.extract_tasks(summaries)

        # 4. Export the final tasks
        exporter = ExportService(config)
        exporter.export_all(refined_tasks)
