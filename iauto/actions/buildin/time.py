import time
from datetime import datetime
from typing import Optional, Union

from ..action import Action, ActionSpec


class WaitAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "time.wait",
            "description": "Waits for a specified number of seconds.",
            "arguments": [
                {
                    "name": "seconds",
                    "type": "float",
                    "description": "The number of seconds to wait.",
                    "required": True
                }
            ]
        })

    def perform(
        self,
        seconds: float,
        **kwargs
    ) -> None:
        if seconds > 0:
            time.sleep(seconds)


class GetNow(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "time.now",
            "description": "Returns the current date and time.",
            "arguments": [
                {
                    "name": "format",
                    "type": "string",
                    "description": "The format string (python format) to format the date and time. If not provided, returns timestamp in milliseconds.",  # noqa: E501
                    "required": False
                }
            ]
        })

    def perform(self, format: Optional[str] = None, **kwargs) -> Union[int, str]:
        now = datetime.now()
        if format is None:
            return int(now.timestamp() * 1000)
        else:
            return now.strftime(format)
