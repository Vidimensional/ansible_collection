# Copyright © 2024 Daniel Vidal de la Rubia <https://github.com/Vidimensional>
#
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the LICENSE file for more details.

import subprocess

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


class SubprocessNonZeroReturnCodeError(Exception):
    def __init__(self, cmd: subprocess.CompletedProcess, *args: object) -> None:
        self.args = cmd.args
        self.stdout = cmd.stdout.decode("utf-8")
        self.stderr = cmd.stderr.decode("utf-8")
        self.returncode = cmd.returncode

        super().__init__(*args)

    pass


def run_module():
    module = AnsibleModule(
        argument_spec={
            "name": {
                "type": "str",
                "required": True,
            },
            "state": {
                "type": "str",
                "default": "present",
                "choices": ["present", "absent"],
            },
            "executable": {
                "type": "str",
                "default": "code",
            },
        },
    )

    name = module.params["name"]
    state = module.params["state"]

    result = {
        "check_mode": module.check_mode,
        "extension_name": name,
        "state": state,
    }

    if module.check_mode:
        result["changed"] = False
        module.l(**result)

    vscode = VSCode(module.params["executable"])

    try:
        r = {}
        if state == "present":
            r = vscode.install_vscode_extension(name)
        elif state == "absent":
            r = vscode.uninstall_vscode_extension(name)

        result |= r
        module.exit_json(**result)

    except SubprocessNonZeroReturnCodeError as e:
        # vscode returned error
        result["cmd_stdout"] = e.stdout
        result["cmd_stderr"] = e.stderr
        result["cmd_returncode"] = e.returncode
        result["args"] = e.args
        module.fail_json("vscode returned error", **result)

    except FileNotFoundError as e:
        # When "executable" doesn't exist or isn't executable
        module.fail_json(str(e))


class VSCode:

    def __init__(self, executable) -> None:
        self.executable = executable

    def list_vscode_extensions(self) -> list[str]:
        resp = subprocess.run(
            [self.executable, "--list-extensions"], capture_output=True
        )
        if resp.returncode != 0:
            raise SubprocessNonZeroReturnCodeError

        return resp.stdout.decode("utf-8").split("\n")

    def install_vscode_extension(self, extension_name: str) -> dict[str, bool]:
        if extension_name in self.list_vscode_extensions():
            return {"changed": False}

        resp = subprocess.run(
            [self.executable, "--install-extension", extension_name],
            capture_output=True,
        )

        if resp.returncode != 0:
            raise SubprocessNonZeroReturnCodeError(resp)

        return {"changed": True}

    def uninstall_vscode_extension(self, extension_name: str) -> dict[str, bool]:
        if extension_name not in self.list_vscode_extensions():
            return {"changed": False}

        resp = subprocess.run(
            [self.executable, "--uninstall-extension", extension_name],
            capture_output=True,
        )

        if resp.returncode != 0:
            raise SubprocessNonZeroReturnCodeError(resp)

        return {"changed": True}


if __name__ == "__main__":
    run_module()
