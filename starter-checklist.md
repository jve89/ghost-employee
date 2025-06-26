# ✅ Starter App Template Checklist

This template is designed to launch **clean, modular, production-grade apps** — AI or non-AI.  
It enforces safe structure, zero clutter, and long-term maintainability from day one.

---

## 🧱 Core Structure

- [x] `app/` — main logic layer
- [x] `config/` — settings, schemas, job configs
- [x] `infrastructure/` — external services, storage, persistence
- [x] `interfaces/` — API, UI, or CLI surface
- [x] `run/` — entrypoints and launch scripts
- [x] `tests/` — clean test suite with `__init__.py`

---

## 🚀 Template Includes

- [x] `.gitpod.yml` for instant workspace spin-up
- [x] `.gitignore` with Python-safe defaults
- [x] `requirements.txt` to track installs (starts empty)
- [x] `filetree.txt` for structure visibility (auto-updatable)
- [x] `makefile` with run, test, lint, format targets
- [x] `README.md` and `LICENSE` for GitHub clarity
- [x] `starter-checklist.md` (this file)
- [x] `scripts/` folder for optional CLI tools or utilities
- [x] `.env.example` placeholder (for dotenv workflows)

---

## 🔁 For Every New Clone

1. Create your project using:


2. Start coding inside existing structure — no setup needed.

3. Keep folders tidy. Every new file must have a home.

4. Update `filetree.txt` regularly to reflect actual structure:

```bash
find . -type d \( -name '__pycache__' -o -name '.git' -o -name 'venv' -o -name '.gitpod' \) -prune -false -o -print | sed 's|[^/]*/|  |g;s|/|- |' > filetree.txt
