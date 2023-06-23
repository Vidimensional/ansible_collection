# Copyright © 2023 Daniel Vidal de la Rubia <https://github.com/Vidimensional>
#
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the LICENSE file for more details.

__metaclass__ = type

DOCUMENTATION = """
    name: github_release
    author: "Daniel Vidal de la Rubia (@vidimensional)"
    short_description: Lookup release information for a given GitHub repository.
    description: |
        - Lookup release information for a given GitHub repository.
        - We can get either the latest release.
        - Or we can get a release that matches
        [python-semanticversion SimpleSpec](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec)
        constrain.
        - Also we can disable the prereleases from the query.
    requirements:
        - '[semantic-version](https://github.com/rbarrois/python-semanticversion)>=2.10.0'
        - '[PyGithub](https://github.com/PyGithub/PyGithub)>=1.58.0'
    options:
        repo:
            description: GitHub repository to query (`USER/REPO_NAME`).
            required: True
            type: string
            default: null
            version_added: 0.0.1
        spec:
            description: >-
                The query for the release to retrieve. It can be `latest` that would retireve the most recent version. Or it can be a
                [`python-semanticversion SimpleSpec`](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec).
            required: False
            type: string
            default: latest
            version_added: 0.0.1
        token:
            description: If provided, it'd be used to send requests to GitHub API. Useful to avoid API request limit errors or accesing private repos.
            required: false
            type: string
            default: None
            version_added: 0.0.1
        allow_prereleases:
            description: If False it'll ignore the releases with [pre-release versions](https://semver.org/spec/v2.0.0.html#spec-item-9).
            type: boolean
            required: false
            default: "False"
            version_added: 0.0.1
"""

EXAMPLES = """
- name: Get the latest Terraform final release.
  ansible.builtin.debug:
    msg: "{{ lookup('vidimensional.collection.github_release', repo='hashicorp/terraform') }}"

- name: Get the latest awscli version(including preseleases).
  ansible.builtin.debug:
    msg: "{{ lookup('vidimensional.collection.github_release', repo='aws/aws-cli', spec='latest', allow_prereleases=True) }}"

- name: Get latest release from a private repo.
  ansible.builtin.debug:
    # ⚠️ Be careful not to send the plain text token to your VCS.
    msg: "{{ lookup('vidimensional.collection.github_release', repo='myorg/some-private-repo',  token='1234') }}"

- name: Get latest Ansible version for branch 2.13
  ansible.builtin.debug:
    msg: "{{ lookup('vidimensional.collection.github_release', repo='ansible/ansible', spec='>=2.13.0,<2.14') }}"
"""

import re

from ansible.errors import AnsibleError
from ansible.errors import AnsibleOptionsError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

try:
    from github import Github
    from github.GithubException import BadCredentialsException
    from semantic_version import Version
    from semantic_version import Spec
except ImportError as err:
    IMPORT_ERROR = err
else:
    IMPORT_ERROR = None

display = Display()


class LookupModule(LookupBase):
    repo = None
    spec = None

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        self.repo = self.get_option("repo")
        self.spec = self.get_option("spec")
        allow_prereleases = self.get_option("allow_prereleases")
        token = self.get_option("token")
        if token == "None":
            token = None

        if IMPORT_ERROR:
            raise AnsibleError(
                f"Required Python library '{IMPORT_ERROR.name}' not installed"
            ) from IMPORT_ERROR

        try:
            versions = fetch_versions_from_github(self.repo, token, allow_prereleases)
        except BadCredentialsException:
            raise AnsibleOptionsError(
                self.format_exception_message("Invalid GitHub token provided.")
            )

        if self.spec == "latest":
            value = max(versions)
        else:
            value = Spec(self.spec).select(versions)

        return [str(value)]

    def format_exception_message(self, msg):
        """'Wraps message adding lookup information. In order to make it easier to identify from where comes the exception.

        Args:
        - `msg` (str): Message to wrap.

        Returns:
        - `str`: Message wrapped with info telling that was lauched from the `github_release` lookup.
        """
        if not self.spec or not self.repo:
            args = ""
        else:
            args = f"', {self.repo}', '{self.spec}'"

        return f"Error from `lookup('github_release{args}, (...))` -> {msg}"


def fetch_versions_from_github(repo_name, token=None, allow_prereleases=False):
    """Fetch the list of tags from the specified GitHub repo.

    Args:
    - `repo_name` (str): The repo where to fetch the tag list. Sould be in the form of username/repo or organization/repo, for example 'aws/aws-cli' would
    reference https://github.com/aws/aws-cli repository.
    - `token` (str): (Optional) If provided, it'd be used to send requests to GitHub API. Useful to avoid API request limit errors.

    Returns:
    - `list[semantic_version.Version]`: The list of versions in GitHub repo, that follows the semver specification.
    """

    gh = Github(token)
    repo = gh.get_repo(repo_name)

    versions = []
    for tag in repo.get_tags():
        try:
            semver = coerce_into_semver(tag.name)
        except ValueError as e:
            display.v(f"ignoring -> {e}")
            continue

        # Ignore prereleases if aren't allowed.
        if not allow_prereleases and semver.prerelease:
            continue

        versions.append(semver)

    return versions


def coerce_into_semver(version_string):
    """Wraps `semantic_version.Version.coerce()` to ensure it correctly coerces versions with string prefix like: v1.2.3 or go1.1rc1.

    Args:
    - `version_string` (str): String representation of the version to coerce.

    Returns:
    - `semantic_version.Version` representation of the input string.

    Raises:
    - `ValueError`: If string provided does not have a valid semver form.
    """

    match = re.match(
        r"^[a-z]*((\d+)(?:\.(\d+)(?:\.(\d+))?)?(?:-?([0-9a-zA-Z.-]*))?(?:\+([0-9a-zA-Z.-]*))?)$",
        version_string,
    )

    if not match:
        raise ValueError(f"String `{version_string}` does not match semver format.")

    return Version.coerce(match.group(1))
