from typing import Any, Optional

from ._action import Action, ActionSpec, Executor, Playbook


class ListAppendAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Add an elements to the end of the list.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if executor is None:
            raise ValueError("executor is None")
        if len(args) != 2:
            raise ValueError("list.append needs 2 args, like: [$list, $value]")

        ls = args[0]
        if isinstance(ls, str) and ls.startswith("$"):
            var = ls
            ls = []
            executor.set_variable(var, ls)

        if not isinstance(ls, list):
            raise ValueError("args[0] is not a list")

        ls.append(args[1])


class DictSetAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Set dict value.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if executor is None:
            raise ValueError("executor is None")
        if len(args) != 3:
            raise ValueError("dict.set needs 2 args, like: [$dict, key, value]")

        d = args[0]
        if isinstance(d, str) and d.startswith("$"):
            var = d
            d = {}
            executor.set_variable(var, d)

        if not isinstance(d, dict):
            raise ValueError("args[0] is not a dict")

        d[args[1]] = args[2]


class DictGetAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Get value from the dictionary. like: dict.get: [$dict, key]",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if len(args) != 2 or not isinstance(args[0], dict):
            raise ValueError("invalid args")
        return args[0].get(args[1])
