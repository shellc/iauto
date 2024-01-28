from typing import Any, Dict

from ._action import Action

_operators = set(["all", "any", "lt", 'le', 'eq', 'ne', 'ge', 'gt'])


def is_operator(d):
    if isinstance(d, Dict) and any([x in _operators for x in d.keys()]):
        return True
    else:
        return False


def eval_operator(operator, vars={}) -> bool:
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
            values[i] = vars.get(v)

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


def eval_operators(operators, vars={}) -> bool:
    if operators is None:
        return False
    elif isinstance(operators, dict):
        return eval_operator(operator=operators, vars=vars)
    elif isinstance(operators, list):
        r = [eval_operators(x) for x in operators]
        return all(r)
    else:
        return bool(operators)


def eval_args(args, kwargs, vars={}):
    if len(args) > 0:
        r1 = eval_operators(args, vars=vars)
    else:
        r1 = True

    if len(kwargs) > 0:
        r2 = eval_operators(kwargs, vars=vars)
    else:
        r2 = True
    return r1 and r2


class RepeatAction(Action):
    def perform(self, executor, playbook, *args, **kwargs: Any) -> None:

        args, kwargs = executor.eval_args(playbook=playbook)
        while eval_args(args, kwargs, vars=executor.variables):
            actions = playbook.get("actions") or []
            for action in actions:
                executor.perform(playbook=action)

            args, kwargs = executor.eval_args(playbook=playbook)


class WhenAction(Action):
    def perform(self, executor, playbook, *args, **kwargs: Any) -> None:
        if eval_args(args, kwargs, vars=executor.variables):
            actions = playbook.get("actions") or []
            for action in actions:
                executor.perform(playbook=action)
