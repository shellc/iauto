from typing import Any, Dict
from ._action import Action
from .._logging import get_logger


class LogAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self._log = get_logger("Log")

    def perform(self, executor=None, playbook=None, **args: Any) -> Dict:
        self._log.info(args)
