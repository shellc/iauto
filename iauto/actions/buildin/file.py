import json
import os
from typing import Any, Dict, List, Optional, Union

from ..action import Action, ActionSpec
from ..loader import register


class FileWriteAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "file.write",
            "description": "Writes the specified content to a file at the given path.",
            "arguments": [
                {
                    "name": "file",
                    "description": "The path to the file where content will be written",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "mode",
                    "description": "The file writing mode ('w' for writing, 'a' for appending, etc.). Defaults to 'w' if not specified.",  # noqa: E501
                    "type": "string",
                    "required": False
                },
                {
                    "name": "cotent",
                    "description": "The content to be written to the file",
                    "type": "string",
                    "required": True
                }
            ]
        })

    def perform(self, file: str, content: Union[str, Dict, List], model: str = "w", **kwargs) -> Any:
        with open(file=file, mode=model) as f:
            if isinstance(content, List) or isinstance(content, Dict):
                content = json.dumps(content, ensure_ascii=False)

            f.write(content)


@register(name="file.exists", spec={
    "description": "Determines if a file exists at the given path.",
    "arguments": [
        {
            "name": "file",
            "description": "The path to the file to be checked for existence.",
            "type": "string",
            "required": True
        }
    ]
})
def file_exists(file: Optional[str] = None, **kwargs) -> bool:
    if file is None:
        raise ValueError(f"invalid args: {file}")
    return os.path.exists(file) and os.path.isfile(file)


@register(name="file.rename", spec={
    "description": "Rename file.",
    "arguments": [

    ]
})
def file_rename(src: str = None, dst: str = None, **kwargs) -> bool:
    return os.rename(src, dst)
