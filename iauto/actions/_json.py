import json
from typing import Any

from ._loader import register_action


@register_action(name="json.loads", spec={
    "description": "JSON deserialize."
})
def loads(*args, **kwargs) -> Any:
    if len(args) != 1:
        raise ValueError(f"Invalid args: {args}")
    return json.loads(args[0])
