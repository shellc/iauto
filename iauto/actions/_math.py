from typing import Any, Dict
from ._action import Action


class ModAction(Action):
    def perform(self, executor=None, playbook=None, **args: Any) -> Dict:
        left = args.get("left")
        right = args.get("right")

        if left is None or right is None:
            raise ValueError(f"Invalid args: {args}")

        return {"result": left % right}
