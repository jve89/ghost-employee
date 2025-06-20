# app/plugins/demo_plugin.py

from app.core.models import Task

class DemoPlugin:
    def can_handle(self, task: Task) -> bool:
        return task.action == "print_report"

    def handle(self, task: Task) -> bool:
        print(f"[DemoPlugin] 🖨️ {task.payload.get('message')}")
        return True
