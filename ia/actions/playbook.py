from typing import Any
from ._action import Action, ActionDef

_definition = ActionDef.from_dict({
    "name": "Playbook",
    "description": "Action playbook"
})


class PlaybookAction(Action):
    def definition(self) -> ActionDef:
        return _definition

    def perform(self, executor=None, actions=None, **args: Any) -> Any:
        if not executor or not actions:
            return

        for action in actions:
            executor.perform(playbook=action)
