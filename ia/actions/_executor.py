from typing import Dict, Any, Tuple
from yaml import load
from yaml import CLoader as yaml_loader
from ._action import Action
from ._loader import loader

VALID_KEYS = ["args", "actions", "return"]


class PlaybookExecutor:
    def __init__(self) -> None:
        self._variables = {}

    def perform(self, playbook: Dict[str, Any]):
        name, action = self.get_action(playbook=playbook)
        args = self.eval_args(playbook=playbook[name])

        returns = action.perform(executor=self, playbook=playbook[name], **args)

        self.eval_return(returns=returns, playbook=playbook[name])

    def get_action(self, playbook: Dict[str, Any]) -> Tuple[str, Action]:
        if playbook is None or not isinstance(playbook, Dict):
            raise ValueError(f"Invalid playbook: {playbook}")

        keys = list(playbook.keys())
        if len(keys) != 1:
            raise ValueError(f"Invalid playbook, more than one Action={keys}")

        name = keys[0]

        playbook_ = playbook[name]

        keys = list(playbook_.keys())
        for k in keys:
            if k not in VALID_KEYS:
                raise ValueError(f"Invalid Action definition: key={k}")

        action = loader.get(name=name)

        if not action:
            raise ValueError(f"Action not found: {name}")

        return name, action

    def eval_args(self, playbook):
        args = playbook.get("args")
        extracted = {}
        if args:
            for k, v in args.items():
                if isinstance(v, str) and v.startswith("$"):
                    extracted[k] = self._variables.get(v)
                else:
                    extracted[k] = v
        return extracted

    def eval_return(self, returns, playbook):
        returns_ = playbook.get("return")
        if returns:
            for k, v in returns_.items():
                if k not in returns:
                    raise ValueError(f"Key error: {k}, returns={returns}")
                r = returns.get(k)

                self._variables[v] = r

    @property
    def variables(self):
        return self._variables

    @staticmethod
    def execute(playbook_file):
        with open(playbook_file, 'r', encoding='utf-8') as f:
            playbook = load(f, Loader=yaml_loader)

        executor = PlaybookExecutor()
        executor.perform(playbook=playbook)
