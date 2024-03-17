import hashlib
import uuid as _uuid

from ..loader import register

namespace = _uuid.uuid1()


@register(name="uuid", spec={
    "description": "Generate a version 5 UUID using SHA1 hash.",
})
def uuid(*args, **kwargs):
    return _uuid.uuid5(namespace, _uuid.uuid1().hex).hex


@register(name="sha1", spec={
    "description": "Generate a SHA1 hash of the given input string.",
    "arguments": [
        {
            "name": "s",
            "type": "string",
            "description": "The input string to hash with SHA1.",
            "required": True
        }
    ],
})
def sha1(s: str, *args, **kwargs):
    m = hashlib.sha1()
    m.update(s.encode())
    return m.digest().hex()


@register(name="sha256", spec={
    "description": "Generate a SHA256 hash of the given input string.",
    "arguments": [
        {
            "name": "s",
            "type": "string",
            "description": "The input string to hash with SHA256.",
            "required": True
        }
    ],
})
def sha256(s: str, *args, **kwargs):
    m = hashlib.sha256()
    m.update(s.encode())
    return m.digest().hex()
