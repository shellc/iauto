import importlib
from typing import List, Dict
from .function import Function


def load_functions(identifiers: List[str] = []) -> Dict[str, Function]:
    functions = {}

    for id in identifiers:
        ss = id.split(".")
        pkg = importlib.import_module('.'.join(ss[:-1]))
        if pkg != '':
            inst = getattr(pkg, ss[-1])()
            functions[id] = inst
    return functions


def get_function_descriptions(functions: Dict[str, Function]) -> List[Dict]:
    return [{"type": "function", "function": f.description()} for f in functions.values()]
