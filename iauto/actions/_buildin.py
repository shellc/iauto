from . import (_browser, _collections, _db, _file, _flow, _hash, _json, _log,
               _math, _playbook, _shell, _time, _webdriver)
from ._loader import loader


def get_buildin_actions():
    actions = {}

    actions["playbook"] = _playbook.PlaybookAction()
    actions["setvar"] = _playbook.SetVarAction()
    actions["log"] = _log.LogAction()
    actions["echo"] = _log.EchoAction()

    actions["repeat"] = _flow.RepeatAction()
    actions["when"] = _flow.WhenAction()
    actions["each"] = _flow.ForEachAction()

    actions["list.append"] = _collections.ListAppendAction()
    actions["dict.set"] = _collections.DictSetAction()
    actions["dict.get"] = _collections.DictGetAction()

    actions["time.wait"] = _time.WaitAction()
    actions["time.now"] = _time.GetNow()

    actions["math.mod"] = _math.ModAction()

    actions["shell.cmd"] = _shell.ShellCommandAction()
    actions["shell.print"] = _shell.PrintAction()
    actions["shell.prompt"] = _shell.PromptAction()
    actions["file.write"] = _file.FileWriteAction()

    actions["browser.open"] = _browser.OpenBrowserAction()
    actions["browser.close"] = _browser.CloseBrowserAction()
    actions["browser.new"] = _browser.NewPageAction()
    actions["browser.goto"] = _browser.GotoAction()
    actions["browser.locator"] = _browser.LocatorAction()
    actions["browser.click"] = _browser.ClickAction()
    actions["browser.scroll"] = _browser.ScrollAction()
    actions["browser.eval"] = _browser.EvaluateJavascriptAction()
    actions["browser.content"] = _browser.GetContentAction()
    actions["browser.readability"] = _browser.ReadabilityAction()

    wd_actions = _webdriver.create_actions()
    actions.update(wd_actions)

    for name, action in actions.items():
        if action.spec.name is None or action.spec.name == 'UNNAMED':
            action.spec.name = name

    return actions


_buildin_actions = get_buildin_actions()

loader.register(_buildin_actions)
