from . import (_browser, _collections, _flow, _log, _math, _playbook, _shell,
               _time, _webdriver)


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
    actions["dict.put"] = _collections.DictPutAction()
    actions["dict.get"] = _collections.DictGetAction()

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
    actions["browser.content"] = _browser.GetContentAction()
    actions["browser.readability"] = _browser.ReadabilityAction()

    wd_actions = _webdriver.create_actions()
    actions.update(wd_actions)

    for name, action in actions.items():
        if action.spec.name is None or action.spec.name == 'UNNAMED':
            action.spec.name = name

    return actions
