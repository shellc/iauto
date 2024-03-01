import json
from typing import Any

from ..loader import register_action


@register_action(name="json.loads", spec={
    "description": "JSON deserialize."
})
def loads(*args, **kwargs) -> Any:
    if len(args) != 1:
        raise ValueError(f"Invalid args: {args}")
    return json.loads(args[0])


@register_action(name="json.load", spec={
    "description": "Deserialize JSON from file."
})
def load(file: str, *args, **kwargs):
    with open(file, "r", encoding="utf-8") as f:
        return json.loads(f.read())
