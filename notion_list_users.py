# notion_list_users.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"

url = "https://api.notion.com/v1/users"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    users = response.json().get("results", [])
    print("\n📋 Notion Users:")
    for user in users:
        name = user.get("name", "No Name")
        user_id = user.get("id", "No ID")
        print(f"- {name}: {user_id}")
else:
    print(f"❌ Failed to retrieve users: {response.status_code} – {response.text}")
