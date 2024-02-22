import json
import os
import sys
from typing import Any

from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from ._action import Action, ActionSpec

_platform = sys.platform
_env = {
    "SHELL": os.environ.get("SHELL"),
    "USER": os.environ.get("USER"),
    "HOME": os.environ.get("HOME"),
    "PWD": os.environ.get("PWD")
}

_spec = ActionSpec.from_dict({
    "name": "shell.cmd",
    "description": f"""Use this tool to execute Linux, macOS, and DOS commands and output the execution results. \
Current OS: {_platform}. \
System Environments: {json.dumps(dict(_env))}""",
    "arguments": [
        {
            "name": "command",
            "type": "string",
            "description": "Command and arguments",
            "required": True
        }
    ]
})


class ShellCommandAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = _spec

    def perform(self, *args, command: str, **kwargs: Any) -> Any:
        try:
            with os.popen(cmd=command) as p:
                return p.read()
        except Exception as e:
            return f"Execute `{command}` failed: {e}"


class PromptAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self._history = InMemoryHistory()

        self.spec = ActionSpec.from_dict({
            "description": "Receive user input from the terminal.",
        })

    def perform(self, *args, **kwargs: Any) -> str:
        p = ''
        if len(args) == 1:
            p = args[0]
        return prompt(p, history=self._history, auto_suggest=AutoSuggestFromHistory(), in_thread=True)


class PrintAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "description": "Print to the terminal.",
        })

    def perform(self, *args, message=None, end="\n", color="", **kwargs) -> None:
        if color.lower() == "red":
            color = "\033[91m"
        elif color.lower() == "green":
            color = "\033[92m"
        elif color.lower() == "yellow":
            color = "\033[93m"
        elif color.lower() == "blue":
            color = "\033[94m"
        elif color.lower() == "purple":
            color = "\033[95m"
        else:
            color = ""

        if color:
            print(color, end='')
        if message:
            print(message, end='')
        else:
            print(end.join(args), end='')
        print(end=end)

        if color:
            print("\033[0m", end='')
