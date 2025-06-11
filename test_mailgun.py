import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into environment

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
DOMAIN = "johanvanerkel.com"

response = requests.post(
    f"https://api.eu.mailgun.net/v3/{DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),  # <- Fixed variable
    data={
        "from": "Ghost Employee <postmaster@johanvanerkel.com>",
        "to": ["jovanerkel@gmail.com"],
        "subject": "✅ Mailgun Test",
        "text": "This is a test from Ghost Employee using the Mailgun EU API."
    }
)

print("Status Code:", response.status_code)
print("Response:", response.text)
