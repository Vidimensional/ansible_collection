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

.PHONY: docs readme
readme: docs
docs:
	ansible-doc -t lookup github_release -M "${PWD}/plugins/lookup/" --json | jq .github_release > /tmp/data.json && \
		j2 -f json README.md.j2 /tmp/data.json > README.md && \
		rm /tmp/data.json

.PHONY: req requirements requirements-dev
req: requirements requirements-dev
requirements:
	python -m pip install -r requirements.txt
requirements-dev:
	python -m pip install -r requirements-dev.txt
