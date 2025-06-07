# app/plugins/crm_plugin.py

import json
import os
import re
from typing import Dict, Any
from datetime import datetime

DUMMY_CRM_PATH = "logs/dummy_crm.json"


class CRMPlugin:
    def can_handle(self, task: Any) -> bool:
        description = (task.description or "").lower()

        # Define simple flexible regex patterns
        patterns = [
            r"\badd\b.*\bcrm\b",
            r"\bupdate\b.*\bcontact\b",
            r"\bcreate\b.*\b(contact|crm)\b",
            r"\bedit\b.*\bcrm\b",
            r"\badd.*to.*crm\b"
        ]

        for pattern in patterns:
            if re.search(pattern, description):
                print(f"[CRMPlugin] ✅ Matched pattern: {pattern} → '{description}'")
                return True

        print(f"[CRMPlugin] ❌ No pattern matched for: '{description}'")
        return False

    def handle(self, task: Any) -> Dict[str, Any]:
        contact_name = task.entity or "Unknown"
        task_description = task.description or ""
        now = datetime.utcnow().isoformat()

        os.makedirs(os.path.dirname(DUMMY_CRM_PATH), exist_ok=True)

        try:
            # Load existing CRM records
            if os.path.exists(DUMMY_CRM_PATH):
                with open(DUMMY_CRM_PATH, "r") as f:
                    crm_data = json.load(f)
            else:
                crm_data = []

            # Try to find existing contact by name (case-insensitive)
            contact_index = next(
                (i for i, c in enumerate(crm_data) if c.get("name", "").lower() == contact_name.lower()),
                None
            )

            if "update" in task_description.lower() or "edit" in task_description.lower():
                if contact_index is not None:
                    crm_data[contact_index].update({
                        "updated_at": now,
                        "last_task": task_description
                    })
                    status_msg = f"CRM entry for {contact_name} updated"
                else:
                    crm_data.append({
                        "name": contact_name,
                        "added_at": now,
                        "task_description": task_description,
                        "note": "Added via update fallback"
                    })
                    status_msg = f"No existing contact found. Added new entry for {contact_name}."
            else:
                crm_data.append({
                    "name": contact_name,
                    "added_at": now,
                    "task_description": task_description
                })
                status_msg = f"CRM entry created for {contact_name}"

            # Write updated CRM file
            with open(DUMMY_CRM_PATH, "w") as f:
                json.dump(crm_data, f, indent=2)

            return {"status": "success", "message": status_msg}

        except Exception as e:
            return {"status": "error", "message": str(e)}
