"""
This module provides the `AgentExecutor` class which is responsible for executing actions on behalf of agents.
It acts as an intermediary layer between the agent's instructions and the actual execution of those instructions.

Classes:
* AgentExecutor
"""
from .executor import AgentExecutor

__all__ = [
    "AgentExecutor"
]
