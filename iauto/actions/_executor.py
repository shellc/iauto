from typing import Any, Dict, Tuple

from yaml import CLoader as yaml_loader
from yaml import load

from ._action import Action
from ._loader import loader

KEY_ARGS = "args"
KEY_ACTIONS = "actions"
KEY_RESULT = "result"
KEY_DESCRIPTION = "description"

VALID_KEYS = [KEY_ARGS, KEY_ACTIONS, KEY_RESULT, KEY_DESCRIPTION]


class PlaybookExecutor:
    def __init__(self) -> None:
        self._variables = {}

    def perform(self, playbook: Dict[str, Any]):
        name, action = self.get_action(playbook=playbook)
        playbook_ = playbook[name]

        args, kwargs = self.eval_args(playbook=playbook_)

        result = action.perform(self, playbook_, *args, **kwargs)

        if isinstance(playbook_, dict):
            self.extract_vars(data=result, playbook=playbook_.get(KEY_RESULT))

    def get_action(self, playbook: Dict[str, Any]) -> Tuple[str, Action]:
        if playbook is None or not isinstance(playbook, Dict):
            raise ValueError(f"Invalid playbook: {playbook}")

        keys = list(playbook.keys())
        if len(keys) != 1:
            raise ValueError(f"Invalid playbook, more than one Action={keys}")

        name = keys[0]

        playbook_ = playbook[name]

        if isinstance(playbook_, dict):
            keys = list(playbook_.keys())
            for k in keys:
                if k not in VALID_KEYS:
                    raise ValueError(f"Invalid Action definition: key={k}")

        action = loader.get(name=name)

        if not action:
            raise ValueError(f"Action not found: {name}")

        return name, action

    def eval_vars(self, playbook):
        if playbook is None:
            return None
        elif isinstance(playbook, str):
            if playbook.startswith("$"):
                return self._variables.get(playbook)
            else:
                return playbook.format(**self._variables)
        elif isinstance(playbook, list):
            return [self.eval_vars(x) for x in playbook]
        elif isinstance(playbook, dict):
            evaled = {}
            for k, v in playbook.items():
                evaled[self.eval_vars(k)] = self.eval_vars(v)
            return evaled
        else:
            return playbook

    def extract_vars(self, data, playbook):
        if playbook is None:
            pass
        elif isinstance(playbook, str) and playbook.strip().startswith("$"):
            self._variables[playbook.strip()] = data
        elif isinstance(playbook, list) and isinstance(data, list):
            for i in range(len(playbook)):
                v = playbook[i]
                if isinstance(v, str) and v.strip().startswith("$") and i < len(data):
                    v = v.strip()
                    self._variables[v] = data[i]
        elif isinstance(playbook, dict) and isinstance(data, dict):
            for k, v in playbook.items():
                if isinstance(k, str) and k.strip().startswith("$"):
                    k = k.strip()
                    self._variables[k] = data.get(v)

    def eval_args(self, playbook):
        args = []
        kwargs = {}

        playbook_ = playbook
        if isinstance(playbook_, dict):
            playbook_ = playbook.get(KEY_ARGS)

        evaled_args = self.eval_vars(playbook=playbook_)

        if evaled_args is not None:
            if isinstance(evaled_args, list):
                args = evaled_args
            elif isinstance(evaled_args, dict):
                kwargs = evaled_args
            else:
                args.append(evaled_args)
        return args, kwargs

    @property
    def variables(self):
        return self._variables

    @staticmethod
    def execute(playbook_file):
        with open(playbook_file, 'r', encoding='utf-8') as f:
            playbook = load(f, Loader=yaml_loader)

        executor = PlaybookExecutor()
        executor.perform(playbook=playbook)
