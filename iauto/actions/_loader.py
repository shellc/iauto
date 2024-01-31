import importlib
from typing import Dict, Union

from ._action import Action


class ActionLoader:
    def __init__(self) -> None:
        self._actions = {}

    def register(self, actions: Dict[str, Action]):
        self._actions.update(actions)

    def get(self, name) -> Union[Action, None]:
        return self._actions.get(name)

    @property
    def actions(self):
        return [a for a in self._actions.values()]

    def load(self, identifier):
        ss = identifier.split(".")
        pkg = importlib.import_module('.'.join(ss[:-1]))
        if pkg != '':
            action = getattr(pkg, ss[-1])()
            name = action.definition.name
            if name in self._actions:
                raise ValueError(f"Action name conflic: {name}")
            self._actions[name] = action


loader = ActionLoader()
