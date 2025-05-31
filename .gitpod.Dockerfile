FROM gitpod/workspace-full

# Optional: pre-install Python packages globally to speed up venv installs
RUN pip install --upgrade pip setuptools wheel
