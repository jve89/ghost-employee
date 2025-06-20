from app.jobs.base_job import BaseJob
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import SimpleExecutor
from app.services.export_dispatcher import dispatch_exports


class HROnboardingAssistantJob(BaseJob):
    def run(self, job_config):
        logger = StructuredLogger(job_config["job_id"])
        logger.info(f"Running job: {job_config['job_name']}")

        # Step 1: Parse tasks
        parser = GPTTaskParser(job_config["gpt_model"])
        parsed = parser.parse_file(job_config["watch_dir"], job_config["file_pattern"])
        if not parsed:
            logger.warning("No content to process.")
            return

        summary = parsed["summary"]
        tasks = parsed["tasks"]
        logger.info("✅ Summary + Tasks extracted")

        # Step 2: Execute tasks
        executor = ExecutorService(job_config)
        execution_results = executor.execute(tasks)
        logger.info("✅ Tasks executed")

        # Step 3: Export
        export_payload = {
            "summary": summary,
            "tasks": tasks,
            "execution_results": execution_results
        }

        exporter = ExportDispatcher(job_config)
        exporter.export(export_payload)
        logger.info("✅ Export complete")
