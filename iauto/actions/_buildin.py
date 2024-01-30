from . import (_browser, _collections, _flow, _log, _math, _shell, _time,
               _webdriver)
from ._playbook import PlaybookAction


def get_buildin_actions():
    actions = {}

    actions["playbook"] = PlaybookAction()
    actions["log"] = _log.LogAction()

    actions["repeat"] = _flow.RepeatAction()
    actions["when"] = _flow.WhenAction()
    actions["each"] = _flow.ForEachAction()

    actions["list.append"] = _collections.ListAppendAction()
    actions["dict.put"] = _collections.DictPutAction()

    actions["time.wait"] = _time.WaitAction()
    actions["time.now"] = _time.GetNowTimestamp()

    actions["math.mod"] = _math.ModAction()

    actions["shell.cmd"] = _shell.ShellCommandAction()
    actions["shell.print"] = _shell.PrintAction()
    actions["shell.prompt"] = _shell.PromptAction()

    actions["browser.open"] = _browser.OpenBrowserAction()
    actions["browser.close"] = _browser.CloseBrowserAction()
    actions["browser.new"] = _browser.NewPageAction()
    actions["browser.goto"] = _browser.GotoAction()
    actions["browser.eval"] = _browser.EvaluateJavascriptAction()

    wd_actions = _webdriver.create_actions()
    actions.update(wd_actions)

    return actions
