from typing import Any, Dict, Optional

from ._action import Action, ActionSpec, Executor, Playbook

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
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Repeat the execution based on specified conditions.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> None:
        if executor is None or playbook is None:
            raise ValueError("executor and playbook can't be None")
        actions = playbook.actions or []

        result = None

        if len(kwargs) == 0 and len(args) == 1 and isinstance(args[0], int):
            for _ in range(args[0]):
                for action in actions:
                    result = executor.perform(playbook=action)
        else:
            args, kwargs = executor.eval_args(args=playbook.args)
            while eval_args(args, kwargs, vars=executor.variables):

                for action in actions:
                    result = executor.perform(playbook=action)

                args, kwargs = executor.eval_args(args=playbook.args)
        return result


class WhenAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Execute actions when the condition is met.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> None:
        if executor is None or playbook is None:
            raise ValueError("executor and playbook can't be None")

        result = None
        if eval_args(args, kwargs, vars=executor.variables):
            actions = playbook.actions or []
            for action in actions:
                result = executor.perform(playbook=action)
        return result


class ForEachAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Execute 'actions' for each element in the set.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if executor is None or playbook is None:
            raise ValueError("executor and playbook can't be None")

        actions = playbook.actions or []
        if len(actions) == 0:
            return

        data = []
        if len(args) > 0:
            if len(args) == 1:
                if isinstance(args[0], list):
                    data = args[0]
                else:
                    data = args
            else:
                data = args
        elif len(kwargs) > 0:
            data = [kwargs]

        result = None
        for i in data:
            executor.set_variable("$_", i)
            for action in actions:
                result = executor.perform(playbook=action)
        return result
