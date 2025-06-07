from datetime import datetime
from app.core.models import Task
from app.core.interfaces import Executor
from app.plugins.file_ops import FileOpsPlugin
from infrastructure.logger.retry_queue import retry_queue

ALL_PLUGINS = [FileOpsPlugin()]

class PluginExecutor(Executor):
    def execute(self, task: Task) -> bool:
        print(f"[PluginExecutor] Executing: {task.description}")
        task.executed_at = datetime.utcnow()

        try:
            for plugin in ALL_PLUGINS:
                if plugin.can_handle(task):
                    result = plugin.handle(task)
                    task.status = "success" if result else "failed"
                    print(f"[PluginExecutor] ✅ Plugin handled task. Success: {result}")
                    return result

            task.status = "skipped"
            print("[PluginExecutor] ❌ No plugin could handle the task.")
            return False

        except Exception as e:
            task.status = "failed"
            retry_queue.add(task, reason=str(e))
            print(f"[PluginExecutor] ❌ Failed: {e}")
            return False
