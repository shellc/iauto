import os
from typing import Any
from ..function import Function


class Ls(Function):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        dir = kwds.get('dir') or '/'
        return os.listdir(dir)

    def description(self) -> dict:
        return {
            "name": "ls",
            "description": "displays the names of files contained within that directory",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "dir": {
                            "type": "string",
                            "description": "the directory to list contents",
                        }
                    },
                "required": ["dir"],
            }
        }
