# app/services/demo_report_generator.py

from datetime import datetime
from pathlib import Path
import markdown2
import pdfkit
import json
from pydantic.json import pydantic_encoder

def generate_demo_report(summary: str, tasks: list, results: list, job_id: str = "demo_job", to_pdf: bool = True) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    export_root = Path(f"exports/{job_id}")
    folder = export_root / f"{timestamp}_GhostRun"
    folder.mkdir(parents=True, exist_ok=True)

    # --- Create summary.md content ---
    content = f"# Ghost Employee Report\n\n"
    content += f"**Job ID:** {job_id}\n"
    content += f"**Generated:** {datetime.now().isoformat()}\n\n"
    content += f"## Summary\n\n{summary.strip()}\n\n"
    content += "## Tasks\n"
    for task in tasks:
        action = task.get("description", "Unknown task")
        status = task.get("status", "pending")
        content += f"- {action} → `{status}`\n"

    content += "\n## Execution Results\n"
    for result in results:
        content += f"- {result.get('description', 'No description')} → `{result.get('status', 'unknown')}`\n"

    # --- Save .md and .pdf ---
    md_path = folder / "summary.md"
    pdf_path = folder / "summary.pdf"
    md_path.write_text(content)
    if to_pdf:
        try:
            pdfkit.from_file(str(md_path), str(pdf_path))
        except OSError as e:
            print(f"[PDFKit] Skipped PDF generation: {e}")

    # --- Save export.json ---
    export_data = {
       "summary": summary,
        "tasks": tasks,
        "results": results,
        "job_name": job_id
    }
    with open(folder / "export.json", "w") as f:
        json.dump(export_data, f, indent=2, default=pydantic_encoder)

    # --- Save metadata.json ---
    metadata = {
        "job_id": job_id,
        "timestamp": timestamp,
        "task_count": len(tasks),
        "success_count": sum(1 for r in results if r.get("status") == "success"),
        "failure_count": sum(1 for r in results if r.get("status") == "failed"),
        "exported_files": ["summary.md", "summary.pdf", "export.json"]
    }
    with open(folder / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return folder
