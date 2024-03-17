import json
import os
import sys
from typing import Any, Optional

from prompt_toolkit import prompt as prompt_func
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from ..action import Action, ActionSpec

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
            "description": "The command to execute, along with any arguments.",
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
            "name": "shell.prompt",
            "description": "Prompt the user for input in the terminal and provide suggestions based on input history.",
            "arguments": [
                {
                    "name": "prompt",
                    "type": "string",
                    "description": "The prompt message to display to the user.",
                    "required": False
                }
            ]
        })

    def perform(self, prompt: Optional[str] = None, **kwargs: Any) -> str:
        prompt = prompt or ""
        return prompt_func(prompt, history=self._history, auto_suggest=AutoSuggestFromHistory(), in_thread=True)


class PrintAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "shell.print",
            "description": "Output a message to the terminal with optional color formatting.",
            "arguments": [
                {
                    "name": "message",
                    "type": "string",
                    "description": "The message to be printed.",
                    "required": False
                },
                {
                    "name": "end",
                    "type": "string",
                    "description": "The end character to append after the message.",
                    "required": False
                },
                {
                    "name": "color",
                    "type": "string",
                    "description": "The color in which the message should be printed. Supported colors: red, green, yellow, blue, purple.",  # noqa: E501
                    "required": False
                }
            ]
        })

    def perform(self, *args, message=None, end="\n", color="", **kwargs) -> None:
        if color.lower() == "red":
            color = "\033[1;31m"
        elif color.lower() == "green":
            color = "\033[1;32m"
        elif color.lower() == "yellow":
            color = "\033[1;33m"
        elif color.lower() == "blue":
            color = "\033[1;34m"
        elif color.lower() == "purple":
            color = "\033[1;35m"
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
