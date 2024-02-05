import hashlib
import uuid as _uuid

from ._loader import register_action

namespace = _uuid.uuid1()


@register_action(name="uuid", spec={
    "description": "Generate UUID."
})
def uuid(*args, **kwargs):
    return _uuid.uuid5(namespace, _uuid.uuid1().hex).hex


@register_action(name="sha1", spec={
    "description": "SHA1"
})
def sha1(s: str, *args, **kwargs):
    m = hashlib.sha1()
    m.update(s.encode())
    return m.digest().hex()


@register_action(name="sha256", spec={
    "description": "SHA1"
})
def sha256(s: str, *args, **kwargs):
    m = hashlib.sha256()
    m.update(s.encode())
    return m.digest().hex()
