# app/core/crm_memory.py

import os
import json

class CRMMemory:
    def __init__(self, job_name: str):
        self.path = f"memory/{job_name}_contacts.json"
        os.makedirs("memory", exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)

    def load_contacts(self) -> list[dict]:
        with open(self.path, "r") as f:
            return json.load(f)

    def save_contacts(self, contacts: list[dict]):
        with open(self.path, "w") as f:
            json.dump(contacts, f, indent=2)

    def contact_exists(self, name: str) -> bool:
        return any(c for c in self.load_contacts() if c.get("name", "").lower() == name.lower())

    def update_contact(self, name: str, phone: str | None = None) -> str:
        contacts = self.load_contacts()
        updated = False
        for c in contacts:
            if c.get("name", "").lower() == name.lower():
                if phone:
                    c["phone"] = phone
                updated = True
                break
        if not updated:
            contacts.append({"name": name, "phone": phone})
        self.save_contacts(contacts)
        return "updated" if updated else "added"
    
    def get_contact(self, name: str) -> dict | None:
        contacts = self.load_contacts()
        for contact in contacts:
            if contact.get("name", "").lower() == name.lower():
                return contact
        return None
    
    def add_contact(self, contact: dict):
        contacts = self.load_contacts()
        contacts.append(contact)
        self.save_contacts(contacts)
