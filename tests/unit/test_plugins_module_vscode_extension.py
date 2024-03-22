# Copyright © 2024 Daniel Vidal de la Rubia <https://github.com/Vidimensional>
#
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the LICENSE file for more details.

import unittest
from unittest.mock import patch
from unittest.mock import Mock

from plugins.module.vscode_extension import run_module


class TestRunModule(unittest.TestCase):

    @patch("plugins.module.vscode_extension.VSCode")
    @patch("plugins.module.vscode_extension.AnsibleModule")
    def test_runmodule_installs_desired_extension(
        self,
        MockedAnsibleModuleConstructor,
        MockedVSCode,
    ):
        vscode_extension_name = "some_vscode_extension"
        vscode_extension_desired_state = "present"
        vscode_executable = "code"
        module_check_mode = False

        MockedVSCode.install_vscode_extension.return_value = {"changed": True}

        MockedAnsibleModule = Mock()
        MockedAnsibleModule.check_mode = module_check_mode
        MockedAnsibleModule.params = {
            "name": vscode_extension_name,
            "state": vscode_extension_desired_state,
            "executable": vscode_executable,
        }

        MockedAnsibleModuleConstructor.return_value = MockedAnsibleModule

        run_module()

        MockedAnsibleModule.exit_json.assert_called_once_with(
            check_mode=module_check_mode,
            extension_name=vscode_extension_name,
            state=vscode_extension_desired_state,
        )


if __name__ == "__main__":
    unittest.main()
