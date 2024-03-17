"""
This module defines the core components of the action system.

It provides the necessary classes and functions to create, manage, and execute actions
within the context of the playbook execution environment. It includes
definitions for actions, action arguments, action specifications, executors, and playbooks.

Classes:
* Action: Represents a single action to be executed.
* ActionArg: Defines an argument that can be passed to an action.
* ActionSpec: Contains the specification details of an action.
* Executor: The base class for action executors.
* Playbook: Represents a sequence of actions to be executed as a unit.
* PlaybookExecutor: Responsible for executing the actions defined in a playbook.
* PlaybookRunAction: A special action that represents the execution of a playbook.

Functions:
* create_action: A factory function to create instances of actions.
* loader: A function to load actions and their specifications.
* register_action: A function to register new actions into the system.

The module also handles the registration and discovery of built-in actions.
"""

from . import buildin, contrib
from .action import Action, ActionArg, ActionSpec, create
from .executor import (Executor, PlaybookExecutor, execute, execute_in_process,
                       execute_in_thread)
from .loader import loader, register
from .playbook import Playbook, load
