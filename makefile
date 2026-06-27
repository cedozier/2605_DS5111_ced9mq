ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip
PYLINT = $(ENV)/bin/pylint
PYTEST = $(ENV)/bin/pytest

.PHONY: default env update lint test test_enrich run run_clean_ids run_extract run_enrich

default:
	@cat makefile

env: $(ENV)/bin/activate

$(ENV)/bin/activate:
	python3 -m venv $(ENV)
	$(PIP) install --upgrade pip

update:  env
	$(PIP) install -r requirements.txt

lint:
	$(PYLINT) bin/ lib/ tests/

test: lint
	$(PYTEST) -vv tests

test_enrich:
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) bin/validate_schema.py

run_clean_ids:
	@cat sample_ids/youtube_ids | $(PYTHON) bin/clean_ids.py

run_extract:
	@cat sample_ids/youtube_ids | $(PYTHON) bin/clean_ids.py | $(PYTHON) bin/extract_transcripts.py

run_enrich:
	@cat sample_ids/youtube_ids | $(PYTHON) bin/clean_ids.py | $(PYTHON) bin/extract_transcripts.py | $(PYTHON) bin/enrich_transcripts.py

run: run_enrich