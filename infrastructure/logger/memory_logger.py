# infrastructure/logger/memory_logger.py

import logging

logger = logging.getLogger("GhostLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

memory_logger = logger  # ✅ Export this so other files can import it
