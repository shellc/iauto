from typing import Any, Dict
from ._action import Action, ActionDef
from .._logging import get_logger


class LogAction(Action):
    def __init__(self) -> None:
        self._log = get_logger("Log")

    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, executor=None, playbook=None, **args: Any) -> Dict:
        self._log.info(args)
