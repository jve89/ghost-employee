import os
import shutil
import re
from app.core.models import Task

class FileOpsPlugin:
    def can_handle(self, task: Task) -> bool:
        """Returns True if this plugin should handle the task"""
        desc = task.description.lower()
        return any(keyword in desc for keyword in ["move", "copy", "rename"])

    def handle(self, task: Task) -> bool:
        """Executes file operation if description contains recognizable action"""
        desc = task.description.lower()
        try:
            if "move" in desc:
                return self._handle_move(desc, task)
            elif "copy" in desc:
                return self._handle_copy(desc, task)
            elif "rename" in desc:
                return self._handle_rename(desc, task)
            else:
                return False
        except Exception as e:
            print(f"[FileOpsPlugin] ❌ Error during file operation: {e}", flush=True)
            return False

    def _handle_move(self, desc, task: Task) -> bool:
        match = re.search(r"move\s+(.*?)\s+to\s+(.*)", desc)
        if not match:
            print("[FileOpsPlugin] ❌ Could not parse move command.")
            return False

        src = match.group(1).strip()
        dst = match.group(2).strip()

        if not os.path.exists(src):
            print(f"[FileOpsPlugin] ❌ File not found: {src}")
            return False

        os.makedirs(dst, exist_ok=True)
        dst_path = os.path.join(dst, os.path.basename(src))
        shutil.move(src, dst_path)
        print(f"[FileOpsPlugin] ✅ Moved '{src}' → '{dst_path}'")
        return True

    def _handle_copy(self, desc, task: Task) -> bool:
        match = re.search(r"copy\s+(.*?)\s+to\s+(.*)", desc)
        if not match:
            print("[FileOpsPlugin] ❌ Could not parse copy command.")
            return False

        src = match.group(1).strip()
        dst = match.group(2).strip()

        if not os.path.exists(src):
            print(f"[FileOpsPlugin] ❌ File not found: {src}")
            return False

        os.makedirs(dst, exist_ok=True)
        dst_path = os.path.join(dst, os.path.basename(src))
        shutil.copy(src, dst_path)
        print(f"[FileOpsPlugin] ✅ Copied '{src}' → '{dst_path}'")
        return True

    def _handle_rename(self, desc, task: Task) -> bool:
        match = re.search(r"rename\s+(.*?)\s+to\s+(.*)", desc)
        if not match:
            print("[FileOpsPlugin] ❌ Could not parse rename command.")
            return False

        src = match.group(1).strip()
        dst = match.group(2).strip()

        if not os.path.exists(src):
            print(f"[FileOpsPlugin] ❌ File not found: {src}")
            return False

        os.rename(src, dst)
        print(f"[FileOpsPlugin] ✅ Renamed '{src}' → '{dst}'")
        return True
