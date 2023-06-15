.PHONY: sanity
sanity:
	rm -rfv tests/output/
	ansible-test sanity -v --venv --redact --python 3.10 --color yes || jq . tests/output/bot/*

.PHONY: docs
docs:
	ansible-doc -t lookup github_release -M "${PWD}/plugins/lookup/" --json | jq .github_release > /tmp/data.json &&  j2 -f json doc/lookup.j2 /tmp/data.json && rm /tmp/data.json
