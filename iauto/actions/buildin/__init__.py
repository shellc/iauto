from ..loader import loader
from . import (collections, db, file, flow, hash, json, log, math, playbook,
               queue, shell, time)

actions = {}

actions["playbook"] = playbook.PlaybookAction()
actions["setvar"] = playbook.SetVarAction()
actions["log"] = log.LogAction()
actions["echo"] = log.EchoAction()

actions["repeat"] = flow.RepeatAction()
actions["when"] = flow.WhenAction()
actions["each"] = flow.ForEachAction()

actions["list.append"] = collections.ListAppendAction()
actions["dict.set"] = collections.DictSetAction()
actions["dict.get"] = collections.DictGetAction()

actions["time.wait"] = time.WaitAction()
actions["time.now"] = time.GetNow()

actions["math.mod"] = math.ModAction()

actions["shell.cmd"] = shell.ShellCommandAction()
actions["shell.print"] = shell.PrintAction()
actions["shell.prompt"] = shell.PromptAction()
actions["file.write"] = file.FileWriteAction()

# for name, action in actions.items():
#    if action.spec.name is None or action.spec.name == 'UNNAMED':
#        action.spec.name = name

loader.register(actions)
