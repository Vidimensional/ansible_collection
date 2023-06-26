.PHONY: sanity
sanity:
	rm -rfv tests/output/
	ansible-test sanity -v --venv --redact --python 3.10 --color yes || jq . tests/output/bot/*

.PHONY: units unit unittest
unit: unittest
units: unittest
unittest:
	cat requirements* > tests/unit/requirements.txt
	ansible-test units -v --venv --python 3.10 --color yes --requirements

.PHONY: docs
docs:
	python scripts/build_docs.py

.PHONY: req requirements requirements-dev
req: requirements requirements-dev
requirements:
	python -m pip install -r requirements.txt
requirements-dev:
	python -m pip install -r requirements-dev.txt
