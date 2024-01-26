import time
from datetime import datetime
from typing import Any, Dict
from ia.actions._action import ActionDef
from ._action import Action


class WaitAction(Action):
    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, **args: Any) -> Dict:
        seconds = args.get("seconds") or 0

        if seconds > 0:
            time.sleep(seconds)


class GetNowTimestamp(Action):
    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, **args: Any) -> Dict:
        return {
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
