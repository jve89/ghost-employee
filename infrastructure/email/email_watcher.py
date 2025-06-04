import imaplib
import email
import os
import time
from threading import Thread
from email.header import decode_header
from dotenv import load_dotenv
from config.config_loader import load_job_configs

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
    # 🔧 Add a fallback:
    if to_email.lower() == "jovanerkel@gmail.com":
        for config in configs:
            if config.job_name == "sample_job":
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
                print(f"[EmailWatcher] Saved: {filepath}")

class EmailWatcher(Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        print(f"[EmailWatcher] Polling inbox every {POLL_INTERVAL} seconds...")
        while True:
            try:
                self.check_inbox()
            except Exception as e:
                print(f"[EmailWatcher] Error: {e}")
            time.sleep(POLL_INTERVAL)

    def check_inbox(self):
        configs = load_job_configs()
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, "UNSEEN")
        mail_ids = data[0].split()

        for mail_id in mail_ids:
            result, message_data = mail.fetch(mail_id, "(RFC822)")
            raw_email = message_data[0][1]
            msg = email.message_from_bytes(raw_email)

            from_email = email.utils.parseaddr(msg.get("From"))[1]
            to_email = email.utils.parseaddr(msg.get("To"))[1]
            subject = clean_subject(msg.get("Subject"))

            if RESTRICT and from_email not in ALLOWED_SENDERS:
                print(f"[EmailWatcher] Skipped email from {from_email}")
                continue

            job_config = get_job_for_recipient(to_email, configs)
            if job_config:
                process_attachments(msg, job_config)
            else:
                print(f"[EmailWatcher] No matching job for: {to_email} / Subject: {subject}")

        mail.logout()
