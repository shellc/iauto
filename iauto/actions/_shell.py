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
    "description": f"""
Use this tool to execute Linux, macOS, and DOS commands and output the execution results.

Current OS: {_platform}
System Environments: {json.dumps(dict(_env), indent=4)}

Examples:
1. Get weather of beijing: curl -s https://wttr.in/beijing
2. open document: open {os.environ.get('HOME')}/Documents/Plans.docx
3. open website: open https://bing.com
    """,
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

    def perform(self, *args, end="\n", **kwargs) -> None:
        print(end.join(args), end=end)
