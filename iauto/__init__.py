"""
`iauto` is a Low-Code intelligent automation tool that integrates LLM and RPA.

Classes:
* Playbook
* PlaybookExecutor
"""

from .actions import (Playbook, PlaybookExecutor, execute, execute_in_process,
                      execute_in_thread, load)
from .agents import _actions
from .llms.actions import register_actions as register_llm_actions

VERSION = "0.1.10"
"""The current version."""

# Register actions

register_llm_actions()

__all__ = [
    "Playbook",
    "PlaybookExecutor"
]
