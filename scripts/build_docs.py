#!/usr/bin/env python

# Copyright © 2023 Daniel Vidal de la Rubia <https://github.com/Vidimensional>
#
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the LICENSE file for more details.

import importlib
import os
import pkgutil
import sys

from types import ModuleType

import jinja2
import yaml


def get_documentation_from_plugin_file(plugin_name: str) -> dict:
    plugin = importlib.import_module(plugin_name)

    return {
        "documentation": yaml.safe_load(plugin.DOCUMENTATION),
        "examples": str(plugin.EXAMPLES),
    }


def get_plugin_type_documentation(plugin_type: ModuleType) -> list[dict]:
    plugins_path = plugin_type.__path__
    sys.path += plugins_path

    return [
        get_documentation_from_plugin_file(pkg.name)
        for pkg in pkgutil.iter_modules(plugins_path)
    ]


class Jinja2TemplateGenerator:
    def __init__(self, j2_env):
        self.j2_env = j2_env

    def generate_readme(self, doc):
        tpl = self.j2_env.get_template("README.md.j2")
        with open("README.md", "w") as md_file:
            md_file.write(tpl.render(doc))

    def generate_plugin_documentation(self, plugin_type, plugins_info):
        tpl = self.j2_env.get_template(f"{plugin_type}.md.j2")
        for plugin in plugins_info:
            plugin_name = plugin["documentation"]["name"]
            with open(f"docs/{plugin_type}_{plugin_name}.md", "w") as md_file:
                md_file.write(tpl.render(plugin))

    def generate_plugins_lookup_documentation(self, plugins_lookup_info):
        self.generate_plugin_documentation("lookup", plugins_lookup_info)


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    lookups_module = importlib.import_module("plugins.lookup")
    doc = {"plugins_lookup": get_plugin_type_documentation(lookups_module)}

    j2 = Jinja2TemplateGenerator(
        jinja2.Environment(
            loader=jinja2.FileSystemLoader(["docs/templates", "."]),
            autoescape=jinja2.select_autoescape(),
        )
    )

    j2.generate_readme(doc)
    j2.generate_plugins_lookup_documentation(doc["plugins_lookup"])
