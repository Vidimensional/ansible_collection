# github_release lookup 

Lookup release information for a given GitHub repository.

- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Examples](#examples)
- [Keyword parameters](#keyword-parameters)
- [Author](#author)

## Synopsis

- Lookup release information for a given GitHub repository.
- We can get either the latest release.
- Or we can get a release that matches
[python-semanticversion SimpleSpec](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec)
constrain.
- Also we can disable the prereleases from the query.


## Requirements

- [semantic-version](https://github.com/rbarrois/python-semanticversion)>=2.10.0
- [PyGithub](https://github.com/PyGithub/PyGithub)>=1.58.0

## Examples

```yaml

- name: Get the latest Terraform final release.
  ansible.builtin.debug:
    msg: "{{ lookup('github_release', repo='hashicorp/terraform') }}"

- name: Get the latest AWS-CLI (including preseleases).
  ansible.builtin.debug:
    msg: "{{ lookup('github_release', repo='aws/aws-cli', spec='latest', allow_prereleases=True) }}"

- name: Get latest release from a private repo.
  ansible.builtin.debug:
    # ⚠️ Be careful not to send the plain text token to your VCS.
    msg: "{{ lookup('github_release', repo='myorg/some-private-repo',  token='1234') }}"

- name: Get latest Ansible version for branch 2.13
  ansible.builtin.debug:
    msg: "{{ lookup('github_release', repo='ansible/ansible', spec='>=2.13.0,<2.14') }}"

```

## Keyword parameters


#### allow_prereleases

- **Description:** If False it'll ignore the releases with [pre-release versions](https://semver.org/spec/v2.0.0.html#spec-item-9).
- **Type:** boolean
- **Required:** False
- **Version added:** 0.0.1


#### repo

- **Description:** GitHub repository to query (`USER/REPO_NAME`).
- **Type:** string
- **Required:** True
- **Version added:** 0.0.1


#### spec

- **Description:** The query for the release to retrieve. It can be `latest` that would retireve the most recent version. Or it can be a [`python-semanticversion SimpleSpec`](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec).
- **Type:** string
- **Required:** False
- **Version added:** 0.0.1


#### token

- **Description:** If provided, it'd be used to send requests to GitHub API. Useful to avoid API request limit errors or accesing private repos.
- **Type:** string
- **Required:** False
- **Version added:** 0.0.1



## Author

- Daniel Vidal de la Rubia ([@vidimensional](https://github.com/Vidimensional))