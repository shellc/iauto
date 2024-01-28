from ._playbook import PlaybookAction
from . import _flow
from . import _log
from . import _time
from . import _math
from . import _shell
from . import _browser


def get_buildin_actions():
    actions = {}

    actions["playbook"] = PlaybookAction()
    actions["log"] = _log.LogAction()

    actions["repeat"] = _flow.RepeatAction()
    actions["when"] = _flow.WhenAction()

    actions["time.wait"] = _time.WaitAction()
    actions["time.now"] = _time.GetNowTimestamp()

    actions["math.mod"] = _math.ModAction()

    actions["shell.command"] = _shell.ShellCommandAction()
    actions["shell.print"] = _shell.PrintAction()
    actions["shell.prompt"] = _shell.PromptAction()

    actions["browser.open"] = _browser.OpenBrowserAction()
    actions["browser.new"] = _browser.NewPageAction()
    actions["browser.goto"] = _browser.GotoAction()
    actions["browser.evaluate"] = _browser.EvaluateJavascriptAction()

    return actions
