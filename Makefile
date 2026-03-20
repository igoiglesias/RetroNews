.PHONY: dev prod superprod install script test cov test-one

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt

dev:
	RETRONEWS_DISABLE_SCHEDULER=1 $(VENV)/bin/fastapi dev app.py

prod:
	$(VENV)/bin/gunicorn app:app -k uvicorn.workers.UvicornWorker -w 1 --bind 0.0.0.0:8000 --access-logfile - --error-logfile -

script:
	$(PYTHON) -m scripts.$(name)

test:
	$(PYTHON) -m pytest tests/ -v

cov:
	$(PYTHON) -m pytest tests/ --cov --cov-report=term-missing --cov-report=html && xdg-open tests/htmlcov/index.html

test-one:
	$(PYTHON) -m pytest $(path) -v
