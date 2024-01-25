import importlib
from typing import List, Dict
from ._action import Action


def load_actions(identifiers: List[str] = []) -> Dict[str, Action]:
    actions = []

    for id in identifiers:
        ss = id.split(".")
        pkg = importlib.import_module('.'.join(ss[:-1]))
        if pkg != '':
            action = getattr(pkg, ss[-1])()
            actions.append(action)

    return actions
