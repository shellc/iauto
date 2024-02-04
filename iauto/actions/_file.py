import json
from typing import Any, Dict, List

from ._action import Action, ActionSpec


class FileWriteAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Write content to a file.",
        })

    def perform(self, *args, file: str, model: str = "w", content: Any, **kwargs: Any) -> Any:
        with open(file=file, mode=model) as f:
            if isinstance(content, List) or isinstance(content, Dict):
                content = json.dumps(content, ensure_ascii=False)

            f.write(content)
