from .actions import Playbook, PlaybookExecutor
from .agents import _actions
from .llms.actions import register_actions as register_llm_actions

VERSION = "0.1.2"


# Register actions

register_llm_actions()

__all__ = [
    "Playbook",
    "PlaybookExecutor"
]
