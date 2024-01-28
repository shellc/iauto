from typing import Any

from ._action import Action, ActionSpec


class PlaybookAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "playbook",
            "description": "Action playbook"
        })

    def perform(self, executor=None, playbook=None, *args, **kwargs) -> Any:
        if not executor or not playbook:
            return

        actions = playbook.get("actions") or []
        for action in actions:
            executor.perform(playbook=action)
