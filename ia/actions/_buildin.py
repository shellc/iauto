from .system import execute_command
from .playbook import PlaybookAction


def get_buildin_actions():
    actions = {}

    actions["execute_command"] = execute_command.ExecuteCommand()
    actions["Playbook"] = PlaybookAction()

    return actions
