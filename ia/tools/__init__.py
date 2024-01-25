import importlib
from typing import List, Dict
from .function import Function


def load_functions(identifiers: List[str] = []) -> Dict[str, Function]:
    functions = []

    for id in identifiers:
        ss = id.split(".")
        pkg = importlib.import_module('.'.join(ss[:-1]))
        if pkg != '':
            func = getattr(pkg, ss[-1])()
            functions.append(func)

    return functions
