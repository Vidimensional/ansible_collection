# Copyright © 2023 Daniel Vidal de la Rubia
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.

__metaclass__ = type

import re

from ansible.errors import AnsibleOptionsError, AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from github import Github
from semantic_version import Version
from semantic_version import Spec


display = Display()


class LookupModule(LookupBase):
    def run(
        self,
        terms: list[str],
        variables: dict[str, str] = None,
        **kwargs: dict[str, str],
    ) -> list[str]:
        try:
            repo, spec = terms
        except ValueError:
            m = "'repository' and 'version_specification' are mandatory values"
            raise AnsibleOptionsError(message=m)

        if "token" in kwargs:
            token = kwargs["token"]
        else:
            token = None

        if "allow_prereleases" in kwargs:
            allow_prereleases = kwargs["allow_prereleases"]
        else:
            allow_prereleases = False

        versions = fetch_versions_from_github(repo, token, allow_prereleases)

        if spec == "latest":
            value = max(versions)
        else:
            value = Spec(spec).select(versions)

        return [str(value)]


def fetch_versions_from_github(
    repo_name: str,
    token: str = None,
    allow_prereleases: bool = False,
) -> list[Version]:
    """Fetch the list of tags from the specified GitHub repo.

    Args:
    - `repo_name` (`str`): The repo where to fetch the tag list. Sould be in the form of username/repo or organization/repo, for example '`aws/aws-cli`' would reference https://github.com/aws/aws-cli repository.
    - `token` (`str`): (Optional) If provided, it'd be used to send requests to GitHub API. Useful to avoid API request limit errors.
    - `allow_prereleases` (`bool`): (Default: False) If True it'll add the tags with pre-release versions (https://semver.org/spec/v2.0.0.html#spec-item-9).

    Returns:
    - `list[semantic_version.Version]`: The list of versions in GitHub repo, that follows the semver specification.
    """

    gh = Github(token)
    repo = gh.get_repo(repo_name)

    versions: list[Version] = []
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


def coerce_into_semver(version_string: str) -> Version:
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


# access_token = "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"
