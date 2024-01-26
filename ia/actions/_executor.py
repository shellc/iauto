from typing import Dict, Any, Tuple
from yaml import load
from yaml import CLoader as yaml_loader
from ._action import Action
from ._loader import loader

VALID_KEYS = ["Args", "Actions", "Returns"]


class PlaybookExecutor:
    def __init__(self) -> None:
        self._variables = {}

    def perform(self, playbook: Dict[str, Any]):
        name, action = self.get_action(playbook=playbook)
        args = self.extract_args(playbook=playbook[name])
        actions = playbook[name].get("Actions")

        returns = action.perform(executor=self, actions=actions, **args)

        self.extract_returns(returns=returns, playbook=playbook[name])

    def get_action(self, playbook: Dict[str, Any]) -> Tuple[str, Action]:
        if playbook is None or not isinstance(playbook, Dict):
            raise ValueError(f"Invalid playbook: {playbook}")

        keys = list(playbook.keys())
        if len(keys) > 1:
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

    def extract_args(self, playbook):
        args = playbook.get("Args")
        extracted = {}
        if args:
            for k, v in args.items():
                if v.startswith("$"):
                    extracted[k] = self._variables.get(v)
                else:
                    extracted[k] = v
        return extracted

    def extract_returns(self, returns, playbook):
        returns_ = playbook.get("Returns")
        if returns:
            for k, v in returns_.items():
                r = returns.get(k)
                if not r:
                    raise ValueError(f"Key error: {k}")

                self._variables[v] = r

    @staticmethod
    def execute(playbook_file):
        with open(playbook_file, 'r', encoding='utf-8') as f:
            playbook = load(f, Loader=yaml_loader)

        executor = PlaybookExecutor()
        executor.perform(playbook=playbook)
