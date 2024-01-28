import time
from datetime import datetime
from typing import Any
from ._action import Action


class WaitAction(Action):
    def perform(self, executor, playbook, *args, **kwargs: Any) -> None:
        if len(args) > 0:
            seconds = args[0]
        elif 'seconds' in kwargs:
            seconds = kwargs['seconds']
        else:
            raise ValueError(f"Invalid args: args={args}, kwargs={kwargs}")

        if seconds > 0:
            time.sleep(seconds)


class GetNowTimestamp(Action):
    def perform(self, *args, **kwargs) -> int:
        return int(datetime.now().timestamp() * 1000)
