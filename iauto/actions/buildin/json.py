import json
from typing import Any

from ..loader import register_action


@register_action(name="json.loads", spec={
    "description": "Convert a JSON-formatted string into a Python object.",
    "arguments": [
        {
            "name": "s",
            "description": "The JSON-encoded string to be deserialized.",
            "type": "string",
            "required": True
        }
    ]
})
def loads(s, **kwargs) -> Any:
    return json.loads(s)


@register_action(name="json.load", spec={
    "description": "Read a JSON file and convert its contents to a Python object.",
    "arguments": [
        {
            "name": "file",
            "description": "The file object representing the JSON file to deserialize.",
            "type": "string",
            "required": True
        }
    ]
})
def load(file: str, **kwargs):
    with open(file, "r", encoding="utf-8") as f:
        return json.loads(f.read())


@register_action(name="json.dumps", spec={
    "description": "Convert a Python object into a JSON-formatted string.",
    "arguments": [
        {
            "name": "obj",
            "description": "The Python object to be serialized as a JSON-encoded string.",
            "type": "object",
            "required": True
        }
    ]
})
def dummps(obj, **kwargs) -> Any:
    return json.dumps(obj=obj, ensure_ascii=True)
