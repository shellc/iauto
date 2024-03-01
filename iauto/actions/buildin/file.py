import json
import os
from typing import Any, Dict, List, Optional

from ..action import Action, ActionSpec
from ..loader import register_action


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


@register_action(name="file.exists", spec={"description": "Test if file exists."})
def file_exists(file: Optional[str] = None, *args, **kwargs) -> bool:
    if file is None and len(args) == 1:
        file = args[0]
    if file is None:
        raise ValueError(f"invalid args: {args}")
    return os.path.exists(file) and os.path.isfile(file)
