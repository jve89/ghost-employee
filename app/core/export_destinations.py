# app/core/export_destinations.py

from enum import Enum

class ExportDestinationType(str, Enum):
    GOOGLE_SHEETS = "google_sheets"
    NOTION = "notion"
    AIRTABLE = "airtable"
    EMAIL = "email"
    FILE = "file"
