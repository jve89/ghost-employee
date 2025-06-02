run:
	uvicorn interfaces.api.main:app --reload --port 8000

watch:
	python run.py

install:
	pip install -r requirements.txt
