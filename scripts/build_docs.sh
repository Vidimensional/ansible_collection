#!/bin/bash

set -euo pipefail
trap 'rm -r ${tmpdir}/' INT TERM EXIT

tmpdir=tmp
docsdir=docs

if [ -d "${tmpdir}" ]; then
    # shellcheck disable=SC2115 # Because we want to expand the *
    rm -r "${tmpdir}"/*
else
    mkdir "${tmpdir}/"
fi

find plugins/lookup/ -iname '*.py' -print0 | xargs --null -I{} -- basename {} .py  | jq -Rs 'split("\n") | map(select(. != "")) | { "lookup": . }' > "${tmpdir}/lookup.json"
# TODO enumerate other type of plugin when needed
# find plugins/othertype/ -iname '*.py' -print0 | xargs --null -I{} -- basename {} .py | jq -Rs 'split("\n") | map(select(. != "")) | { "othertype": . }' > "${tmpdir}/othertype.json"

jq -s add "${tmpdir}"/*.json > "${tmpdir}/index.json"

j2 -f json "${docsdir}/templates/index.md.j2" "${tmpdir}/index.json" > "${docsdir}/index.md"

# Generate lookup docs
for item in $(jq -r '.lookup[]' "${tmpdir}/index.json"); do
    ansible-doc -t lookup "${item}" -M "${PWD}/plugins/lookup/" --json | jq ".${item}" > "${tmpdir}/${item}.json"
    j2 -f json "${docsdir}/templates/lookup.md.j2" "${tmpdir}/${item}.json" > "${docsdir}/lookup_${item}.md"
done
