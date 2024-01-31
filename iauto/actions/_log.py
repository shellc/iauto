from typing import Any, Optional

from .._logging import get_logger
from ._action import Action, Executor, Playbook


class LogAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self._log = get_logger("Log")

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> None:
        message = ""

        if len(args) > 0:
            message += ', '.join([str(x) for x in args])

        if len(kwargs) > 0:
            message += str(kwargs)

        self._log.info(message)


class EchoAction(Action):
    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if len(args) > 0:
            return args
        elif len(kwargs) > 0:
            return kwargs
        else:
            return None
