from typing import Dict, Any, Tuple
from yaml import load
from yaml import CLoader as yaml_loader
from ._action import Action
from ._loader import loader

VALID_KEYS = ["args", "actions", "result", "description"]


class PlaybookExecutor:
    def __init__(self) -> None:
        self._variables = {}

    def perform(self, playbook: Dict[str, Any]):
        name, action = self.get_action(playbook=playbook)
        args = self.eval_args(playbook=playbook[name])

        result = action.perform(executor=self, playbook=playbook[name], **args)

        self.eval_result(result=result, playbook=playbook[name])

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

    def eval_result(self, result, playbook):
        result_ = playbook.get("result")
        if result:
            for k, v in result_.items():
                if k not in result:
                    raise ValueError(f"Key error: {k}, result={result}")
                r = result.get(k)

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
