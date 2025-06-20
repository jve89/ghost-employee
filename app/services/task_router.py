# app/services/task_router.py

from app.core.models import Task
from app.plugins.crm_plugin import handle_crm_task
from app.plugins.hr_plugin import handle_hr_task
from app.plugins.demo_plugin import handle_demo_task
from infrastructure.logger.memory_logger import memory_logger

import logging
logger = logging.getLogger(__name__)

def route_task(task: Task) -> bool:
    """
    Try handling the task with all known plugins.
    Returns True if a plugin handled it, False otherwise.
    """
    description = task.description.lower().strip()

    # 🔍 Try HR Plugin
    success, message = handle_hr_task(description)
    logger.info(message)
    memory_logger.log("HRPlugin", message)
    if success:
        return True

    # 🔍 Try CRM Plugin
    success, message = handle_crm_task(description)
    logger.info(message)
    memory_logger.log("CRMPlugin", message)
    if success:
        return True

    # 🔍 Try Demo Plugin (fallback dev stub)
    success, message = handle_demo_task(description)
    logger.info(message)
    memory_logger.log("DemoPlugin", message)
    if success:
        return True

    return False  # No plugin matched
