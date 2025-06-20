# app/plugins/demo_plugin.py

from app.core.models import Task

class DemoPlugin:
    def can_handle(self, task: Task) -> bool:
        return task.action == "print_report"

    def handle(self, task: Task) -> bool:
        print(f"[DemoPlugin] 🖨️ {task.payload.get('message')}")
        return True

def handle_demo_task(description: str) -> tuple[bool, str]:
    """
    Simple handler for demo tasks.
    Matches if 'demo' or 'test' appears in the task description.
    """
    if "demo" in description.lower() or "test" in description.lower():
        return True, f"[DemoPlugin] ✅ Handled demo task: {description}"

    return False, "[DemoPlugin] ❌ No match in Demo plugin."