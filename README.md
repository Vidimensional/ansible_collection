# github_release lookup

Lookup release information for a given GitHub repository.

- [github\_release lookup](#github_release-lookup)
  - [Synopsis](#synopsis)
  - [Parameters](#parameters)
  - [Keyword parameters](#keyword-parameters)
  - [Examples](#examples)
  - [Author](#author)

## Synopsis

- Lookup release information for a given GitHub repository.
- We can get either the latest release.
- Or we can get a release that matches
  [python-semanticversion SimpleSpec](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec)
- Also we can disable the prereleases from the query.

## Parameters

#### 1

- **Description:** GitHub repository to query (`USER/REPO_NAME`).
- **Type:** string
- **Required:** True
- **Version added:** 0.0.1

#### 2

- **Description:** The query for the release to retrieve.It can be `latest` that would retireve the most recent version. Or it can be a [`python-semanticversion`](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec) range specification.
- **Type:** string
- **Required:** True
- **Version added:** 0.0.1
- **Choices:**
  - latest
  - range specification

## Keyword parameters

#### allow_prereleases

- **Description:** If False it'll ignore the releases with [pre-release versions](https://semver.org/spec/v2.0.0.html#spec-item-9).
- **Type:** boolean
- **Required:** False
- **Version added:** 0.0.1

#### token

- **Description:** If provided, it'd be used to send requests to GitHub API. Useful to avoid API request limit errors or accesing private repos.
- **Type:** string
- **Required:** False
- **Version added:** 0.0.1

## Examples

```yaml
- name: Get the latest Terraform final release.
  ansible.builtin.debug:
    msg: "{{ lookup('github_release', 'hashicorp/terraform', 'latest') }}"

- name: Get the latest AWS-CLI (including preseleases).
  ansible.builtin.debug:
    msg: "{{ lookup('github_release', 'aws/aws-cli', 'latest', allow_prereleases=True) }}"
```

## Author

- Daniel Vidal de la Rubia ([@vidimensional](https://github.com/Vidimensional))
