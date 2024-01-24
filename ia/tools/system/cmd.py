import os
from typing import Any
from ..function import Function


class Command(Function):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        cmd = kwds.get('command')
        with os.popen(cmd=cmd) as p:
            return p.read()

    def description(self) -> dict:
        return {
            "name": "command",
            "description": "execute Linux, macOS, and DOS commands and output the execution results",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command and arguments",
                        }
                    },
                "required": ["command"],
            }
        }
