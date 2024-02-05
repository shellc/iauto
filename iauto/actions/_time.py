import time
from datetime import datetime
from typing import Optional, Union

from ._action import Action, ActionSpec, Executor, Playbook


class WaitAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "description": "Wait for a specified seconds.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> None:
        if len(args) > 0:
            seconds = args[0]
        elif 'seconds' in kwargs:
            seconds = kwargs['seconds']
        else:
            raise ValueError(f"Invalid args: args={args}, kwargs={kwargs}")

        if seconds > 0:
            time.sleep(seconds)


class GetNow(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "description": "Get the current datetime.",
        })

    def perform(self, *args, format: Optional[str] = None, **kwargs) -> Union[int, str]:
        now = datetime.now()
        if format is None:
            return int(now.timestamp() * 1000)
        else:
            return now.strftime(format)
