# Copyright © 2023 Daniel Vidal de la Rubia
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.

import unittest
from unittest.mock import patch
from unittest.mock import Mock

from plugins.lookup.github_release import coerce_into_semver
from plugins.lookup.github_release import fetch_versions_from_github

from semantic_version import Version


class TestFetchVersionsFromGithub(unittest.TestCase):
    repo_tags = ["6.6.6", "1.1.1-beta1", "0.1.2-rc1", "10.10.10+asdf"]

    @patch("plugins.lookup.github_release.Github")
    def test_fetch_versions_from_github_ignore_prereleases(self, MockedGitHubClient):
        MockedGitHubClient.return_value = self.mocked_github_client(self.repo_tags)

        self.assertEqual(
            [
                Version("6.6.6"),
                Version("10.10.10+asdf"),
            ],
            fetch_versions_from_github(
                "repo",
                "token",
                allow_prereleases=False,
            ),
        )

    @patch("plugins.lookup.github_release.Github")
    def test_fetch_versions_from_github_include_prereleases(self, MockedGitHubClient):
        MockedGitHubClient.return_value = self.mocked_github_client(self.repo_tags)

        self.assertEqual(
            [
                Version("6.6.6"),
                Version("1.1.1-beta1"),
                Version("0.1.2-rc1"),
                Version("10.10.10+asdf"),
            ],
            fetch_versions_from_github(
                "repo",
                "token",
                allow_prereleases=True,
            ),
        )

    def mocked_github_client(self, repo_tags):
        """Returns a `unittest.mock.Mock` implementig the methods of `github.Github` used in `plugins.lookup.github_release`.

        Args:
        - `repo_tags` (`str`): Name of the tags that the mocked client repo should return for the repo.

        Returns:
        - A `unittest.mock.Mock` implementig the methods of `github.Github` used in `plugins.lookup.github_release`.
        """
        tag_list = []
        for name in repo_tags:
            tag = Mock()
            tag.name = name
            tag_list.append(tag)

        gh = Mock()
        mocked_repo = gh.get_repo.return_value
        mocked_repo.get_tags.return_value = tag_list
        return gh


class TestCoerceIntoSemver(unittest.TestCase):
    def test_coerce_into_semver(self):
        cases = {
            "1": Version("1.0.0"),
            "1.1": Version("1.1.0"),
            "1.1.1": Version("1.1.1"),
            "1-pre": Version("1.0.0-pre"),
            "1.1-pre": Version("1.1.0-pre"),
            "1.1.1-pre": Version("1.1.1-pre"),
            "1+build": Version("1.0.0+build"),
            "1.1+build": Version("1.1.0+build"),
            "1.1.1+build": Version("1.1.1+build"),
            "1-pre+build": Version("1.0.0-pre+build"),
            "1.1-pre+build": Version("1.1.0-pre+build"),
            "1.1.1-pre+build": Version("1.1.1-pre+build"),
            "prefix1": Version("1.0.0"),
            "prefix1.1": Version("1.1.0"),
            "prefix1.1.1": Version("1.1.1"),
            "prefix1-pre": Version("1.0.0-pre"),
            "prefix1.1-pre": Version("1.1.0-pre"),
            "prefix1.1.1-pre": Version("1.1.1-pre"),
            "prefix1+build": Version("1.0.0+build"),
            "prefix1.1+build": Version("1.1.0+build"),
            "prefix1.1.1+build": Version("1.1.1+build"),
            "prefix1-pre+build": Version("1.0.0-pre+build"),
            "prefix1.1-pre+build": Version("1.1.0-pre+build"),
            "prefix1.1.1-pre+build": Version("1.1.1-pre+build"),
        }

        for c in cases:
            self.assertEqual(cases[c], coerce_into_semver(c))


if __name__ == "__main__":
    unittest.main()
