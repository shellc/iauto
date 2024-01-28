from typing import Any
from ._action import Action
from .._logging import get_logger


class LogAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self._log = get_logger("Log")

    def perform(self, executor, playbook, *args, **kwargs: Any) -> None:
        message = ""

        if len(args) > 0:
            message += ', '.join([str(x) for x in args])

        if len(kwargs) > 0:
            message += str(kwargs)

        self._log.info(message)
