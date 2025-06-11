# app/plugins/crm_plugin.py

import json
import os
import re
from typing import Dict, Any
from datetime import datetime
from app.core.crm_memory import CRMMemory

DUMMY_CRM_PATH = "logs/dummy_crm.json"


class CRMPlugin:
    def can_handle(self, task: Any) -> bool:
        description = (task.description or "").lower()

        # Expanded regex patterns to match more real-world CRM/admin task phrases
        patterns = [
            # CRM contacts
            r"\badd\b.*\b(crm|customer relationship management)\b",
            r"\b(update|edit|amend|modify|change)\b.*\b(contact|entry|record)\b",
            r"\bassign\b.*\b(contact|representative|liaison|manager)\b",
            r"\b(set|mark)\b.*\bas\b.*\b(contact|liaison|rep|representative)\b",
            r"\bmake\b.*\b(contact|liaison)\b.*\bfor\b.*\b\w+",

            # Onboarding / HR admin
            r"\bcomplete\b.*\bonboarding form\b",
            r"\bsend\b.*\bonboarding documents\b",
            r"\bschedule\b.*\borientation\b",
            r"\bbook\b.*\bintro call\b",
            r"\binitiate\b.*\b(employee|staff)? onboarding\b",

            # CRM task follow-up
            r"\bcheck in\b.*\b(client|lead)\b",
            r"\bfollow up\b.*\b(client|lead|prospect)\b",
            r"\bsend\b.*\bwelcome (email|message)\b",
            r"\bassign\b.*\blead\b",
            r"\bcreate\b.*\b(new )?(client|lead) profile\b"
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

        # Try to extract role and company (very basic)
        role_match = re.search(r"\b(as|is|to be|becomes)\b\s+(the\s+)?(?P<role>\w+\s+\w+)", task_description.lower())
        company_match = re.search(r"\b(at|for|from)\b\s+(?P<company>[A-Z][\w\s&-]+)", task_description)

        role = role_match.group("role").strip() if role_match else None
        company = company_match.group("company").strip() if company_match else None

        try:
            crm_memory = CRMMemory(job_name=task.job_id or "crm_ops_job")
            existing = crm_memory.get_contact(contact_name)

            if "update" in task_description.lower() or "edit" in task_description.lower():
                if existing:
                    update_data = {
                        "updated_at": now,
                        "last_task": task_description
                    }
                    if role:
                        update_data["role"] = role
                    if company:
                        update_data["company"] = company
                    crm_memory.update_contact(contact_name, update_data)
                    msg = f"CRM entry for {contact_name} updated"
                else:
                    contact_data = {
                        "name": contact_name,
                        "added_at": now,
                        "task_description": task_description,
                        "note": "Added via update fallback"
                    }
                    if role:
                        contact_data["role"] = role
                    if company:
                        contact_data["company"] = company
                    crm_memory.add_contact(contact_data)
                    msg = f"No existing contact found. Added new entry for {contact_name}."
            else:
                contact_data = {
                    "name": contact_name,
                    "added_at": now,
                    "task_description": task_description
                }
                if role:
                    contact_data["role"] = role
                if company:
                    contact_data["company"] = company
                crm_memory.add_contact(contact_data)
                msg = f"CRM entry created for {contact_name}"

            return {"status": "success", "message": msg}

        except Exception as e:
            return {"status": "error", "message": str(e)}
