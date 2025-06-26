import os
import openai
import logging

openai.api_key = os.getenv("OPENAI_API_KEY")
DISABLE_GPT = os.getenv("DISABLE_GPT", "false").lower() == "true"

def parse_tasks_with_gpt(text: str, job_id: str) -> dict:
    if DISABLE_GPT:
        logging.warning("🔌 GPT is disabled. Returning mock response.")
        return {
            "summary": f"(GPT DISABLED) Mock summary for job: {job_id}",
            "tasks": [
                {
                    "description": "Mock task: forward report to client",
                    "action": "send_email",
                    "priority": "high"
                },
                {
                    "description": "Mock task: log file in system",
                    "action": "log",
                    "priority": "medium"
                }
            ]
        }

    try:
        prompt = f"Analyse this text for tasks:\n{text}\n\nRespond with summary and structured task list."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You extract tasks and summarise corporate messages."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response["choices"][0]["message"]["content"]
        # TODO: Parse content into structured dict if needed
        return {
            "summary": content[:300],  # Trimmed
            "tasks": []  # You can add a structured parse if needed
        }

    except Exception as e:
        logging.error(f"❌ GPT API call failed: {e}")
        return {
            "summary": f"(Error) Failed to parse via GPT: {str(e)}",
            "tasks": []
        }
