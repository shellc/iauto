import queue

from ..loader import register


@register(name="queue.create", spec={
    "description": "Create a queue"
})
def create_queue(**kwargs):
    return queue.Queue()


@register(name="queue.put", spec={
    "description": "Put item into the queue.",
    "arguments": [
        {
            "name": "item",
            "type": "object",
            "description": "The object will be put into the queue.",
            "required": True
        }
    ]
})
def put(q: queue.Queue, item, **kwargs):
    return q.put(item, block=False)


@register(name="queue.get", spec={
    "description": "Remove and return an item from the queue.",
    "arguments": [
        {
            "name": "block",
            "type": "bool",
            "description": "If true, block until an item is available, otherwise return an item or None",
            "required": False
        }
    ]
})
def get(q: queue.Queue, block: bool = True, **kwargs):
    try:
        return q.get(block=block)
    except queue.Empty:
        return None
