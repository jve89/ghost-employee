from infrastructure.exporters.notion_exporter import NotionExporter

exporter = NotionExporter(config={}, job_id="crm_ops_job_test")

mock_data = {
    "summary": "Test summary for multiple task export.",
    "source_file": "test_file.txt",
    "tasks": [
        {
            "description": "Complete onboarding form",
            "assignee": "Johan",
            "due_date": "2025-06-12"
        },
        {
            "description": "Schedule orientation",
            "assignee": "Alex",
            "due_date": "2025-06-13"
        },
        {
            "description": "⚠️ Invalid priority trigger",
            "assignee": "Lisa",
            "due_date": "2025-06-14",
            "priority": "Critical"  # NOT supported in Notion config
        }
    ]
}

exporter.export(output_data=mock_data, config={})
