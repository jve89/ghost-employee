import imaplib
import email
import os
import time
import socket
from threading import Thread
from email.header import decode_header
from dotenv import load_dotenv
from config.config_loader import load_job_configs
from app.core.email_pipeline import process_email_content

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
POLL_INTERVAL = int(os.getenv("EMAIL_POLL_INTERVAL", 60))
ALLOWED_SENDERS = os.getenv("ALLOWED_SENDERS", "").split(",")
RESTRICT = os.getenv("RESTRICT_EMAIL_OUTPUTS", "off") == "on"

SUPPORTED_EXTENSIONS = (".txt", ".csv", ".docx", ".pdf")

def clean_subject(subject):
    try:
        decoded, charset = decode_header(subject)[0]
        return decoded.decode(charset or "utf-8") if isinstance(decoded, bytes) else decoded
    except:
        return subject

def get_job_for_recipient(to_email, configs):
    for config in configs:
        if to_email.lower().startswith(config.job_name.lower()):
            return config
    if to_email.lower() == "jovanerkel@gmail.com":
        for config in configs:
            if config.job_name == "compliance_analyst":
                return config
    return None

def process_attachments(msg, job_config):
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename and filename.lower().endswith(SUPPORTED_EXTENSIONS):
                filepath = os.path.join(job_config.watch_dir, filename)
                os.makedirs(job_config.watch_dir, exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print(f"[EmailWatcher] ✅ Saved: {filepath}", flush=True)

def safe_connect():
    try:
        print("[EmailWatcher] Connecting to IMAP...", flush=True)
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=10)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        return mail
    except socket.timeout:
        print("[EmailWatcher] ❌ Connection timed out.", flush=True)
    except Exception as e:
        print(f"[EmailWatcher] ❌ IMAP connection failed: {e}", flush=True)
    return None

class EmailWatcher(Thread):
    def __init__(self):
        super().__init__()
        self.started = False

    def run(self):
        self.started = True
        self.poll_loop()

    def start_and_wait(self):
        self.start()
        while not self.started:
            time.sleep(0.1)
    
    def start_in_main_thread(self):
        self.started = True
        self.poll_loop()

    def poll_loop(self):
        print("🟢 EmailWatcher is ACTIVE — polling inbox...", flush=True)
        print(f"[EmailWatcher] Polling every {POLL_INTERVAL} seconds.", flush=True)

        self.check_inbox()  # Run once immediately

        while True:
            try:
                time.sleep(POLL_INTERVAL)
                self.check_inbox()
            except Exception as e:
                print(f"[EmailWatcher] ❌ Error during polling: {e}", flush=True)

    def check_inbox(self):
        configs = load_job_configs()
        mail = safe_connect()
        if not mail:
            return

        try:
            result, data = mail.search(None, "ALL")
            if result != "OK":
                print(f"[EmailWatcher] ⚠️ Inbox search failed: {result}", flush=True)
                return

            mail_ids = data[0].split()
            for mail_id in mail_ids:
                result, message_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = message_data[0][1]
                msg = email.message_from_bytes(raw_email)

                from_email = email.utils.parseaddr(msg.get("From"))[1]
                to_email = email.utils.parseaddr(msg.get("To"))[1]
                subject = clean_subject(msg.get("Subject"))

                # Extract plain text email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain" and part.get_payload(decode=True):
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                if RESTRICT and from_email not in ALLOWED_SENDERS:
                    continue

                job_config = get_job_for_recipient(to_email, configs)
                if job_config:
                    process_attachments(msg, job_config)  # Optional, keep saving files

                    job_config = job_config.dict()  # Convert to a plain dict
                    job_config["sender"] = from_email

                    process_email_content(subject, body, job_config)

                else:
                    print(f"[EmailWatcher] No matching job for: {to_email} / Subject: {subject}", flush=True)
        
        finally:
            mail.logout()
