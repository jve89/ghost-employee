run:
	uvicorn interfaces.api.routes.app_main:app --reload

test:
	pytest tests

lint:
	flake8 app config infrastructure interfaces tests

format:
	black app config infrastructure interfaces tests
