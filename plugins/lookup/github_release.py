# Copyright © 2023 Daniel Vidal de la Rubia <https://github.com/Vidimensional>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.

__metaclass__ = type

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
        try:
            self.repo, self.spec = terms
        except ValueError:
            raise AnsibleOptionsError(
                self.format_exception_message(
                    "'repository' and 'version_specification' are mandatory values."
                )
            )

        if IMPORT_ERROR:
            raise AnsibleError(
                f"Required Python library '{IMPORT_ERROR.name}' not installed"
            ) from IMPORT_ERROR

        if "token" in kwargs:
            token = kwargs["token"]
        else:
            token = None

        if "allow_prereleases" in kwargs:
            allow_prereleases = kwargs["allow_prereleases"]
        else:
            allow_prereleases = False

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
        if not self.spec or not self.repo:
            args = ""
        else:
            args = f"', {self.repo}', '{self.spec}'"

        return f"Error from `lookup('github_release{args}, (...))` -> {msg}"


def fetch_versions_from_github(repo_name, token=None, allow_prereleases=False):
    """Fetch the list of tags from the specified GitHub repo.

    Args:
    - `repo_name` (`str`): The repo where to fetch the tag list. Sould be in the form of username/repo or organization/repo, for example '`aws/aws-cli`'
    would reference https://github.com/aws/aws-cli repository.
    - `token` (`str`): (Optional) If provided, it'd be used to send requests to GitHub API. Useful to avoid API request limit errors.
    - `allow_prereleases` (`bool`): (Default: False) If True it'll add the tags with pre-release versions (https://semver.org/spec/v2.0.0.html#spec-item-9).

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
    """Wraps `semantic_version.Version.coerce()` to ensure it correctly coerces versions with string prefix like: v1.2.3 or go1.1rc1

    Args:
    - `version_string` (`str`): String representation of the version to coerce.

    Returns:
    - `semantic_version.Version` representation of the input string.

    Raises:
    - `ValueError`: If string provided does not match with a valid semver.
    """

    match = re.match(
        r"^[a-z]*((\d+)(?:\.(\d+)(?:\.(\d+))?)?(?:-?([0-9a-zA-Z.-]*))?(?:\+([0-9a-zA-Z.-]*))?)$",
        version_string,
    )

    if not match:
        raise ValueError(f"String `{version_string}` does not match semver format.")

    return Version.coerce(match.group(1))
