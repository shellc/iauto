from .system import execute_command
from .playbook import PlaybookAction
from . import _flow as flow
from . import _log as log
from . import _time
from . import _math


def get_buildin_actions():
    actions = {}

    actions["execute_command"] = execute_command.ExecuteCommand()
    actions["playbook"] = PlaybookAction()
    actions["log"] = log.LogAction()

    actions["while"] = flow.WhileAction()
    actions["if"] = flow.IfAction()

    actions["wait"] = _time.WaitAction()
    actions["get_now_timestamp"] = _time.GetNowTimestamp()

    actions["mod"] = _math.ModAction()

    return actions
