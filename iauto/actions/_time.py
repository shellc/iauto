import time
from datetime import datetime
from typing import Any, Dict
from ._action import Action


class WaitAction(Action):
    def perform(self, **args: Any) -> Dict:
        seconds = args.get("seconds") or 0

        if seconds > 0:
            time.sleep(seconds)


class GetNowTimestamp(Action):
    def perform(self, **args: Any) -> Dict:
        return {
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
