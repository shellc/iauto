from typing import Any, Dict
from ._action import Action


_operators = set(["all", "any", "lt", 'le', 'eq', 'ne', 'ge', 'gt'])


def is_operator(d):
    if isinstance(d, Dict) and any([x in _operators for x in d.keys()]):
        return True
    else:
        return False


def eval_operator(operator, variables={}) -> bool:
    """
    all: all true
    any: any is true
    lt: less than
    le: less than or equal to
    eq: equal to
    ne: not equal to
    ge: greater than or equal to
    gt: greater than
    """
    if not isinstance(operator, Dict) or len(operator) != 1:
        raise ValueError(f"Invalid operator: {operator}")

    o = list(operator.keys())[0]

    if o not in _operators:
        raise ValueError(f"Invalid operator: {o}")

    values = operator.get(o) or []
    values = values[::]

    if not (o == "all" or o == "any") and len(values) != 2:
        raise ValueError(f"operator reqiures 2 args: {operator}")

    for i in range(len(values)):
        v = values[i]
        if v is not None and isinstance(v, str) and v.startswith("$"):
            values[i] = variables.get(v)

    if o == "all" or o == "any":
        results = []
        for v in values:
            if is_operator(v):
                r = eval_operator(v)
            else:
                r = bool(v)
            results.append(r)
        if o == "all":
            return all(results)
        elif o == "any":
            return any(results)
        else:
            raise ValueError(f"Bug: {operator}")
    elif o == "lt":
        return values[0] < values[1]
    elif o == "le":
        return values[0] <= values[1]
    elif o == "eq":
        return values[0] == values[1]
    elif o == "ne":
        return values[0] != values[1]
    elif o == "ge":
        return values[0] >= values[1]
    elif o == "gt":
        return values[0] > values[1]
    else:
        raise ValueError(f"Bug: {operator}")


class WhileAction(Action):
    def perform(self, executor, playbook, **args: Any) -> Dict:
        args = executor.eval_args(playbook)

        while eval_operator(args, variables=executor.variables):
            actions = playbook.get("actions") or []
            for action in actions:
                executor.perform(playbook=action)

            args = executor.eval_args(playbook)


class IfAction(Action):
    def perform(self, executor, playbook, **args: Any) -> Dict:
        args = executor.eval_args(playbook)

        if eval_operator(args, variables=executor.variables):
            actions = playbook.get("actions") or []
            for action in actions:
                executor.perform(playbook=action)
