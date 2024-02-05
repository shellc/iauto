from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple, Union

from ._action import Action, Executor, Playbook
from ._loader import ActionLoader, loader

KEY_ARGS = "args"
KEY_ACTIONS = "actions"
KEY_RESULT = "result"
KEY_DESCRIPTION = "description"

VALID_KEYS = [KEY_ARGS, KEY_ACTIONS, KEY_RESULT, KEY_DESCRIPTION]


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


class PlaybookExecutor(Executor):
    def __init__(self) -> None:
        super().__init__()
        self._action_loader = ActionLoader()
        self._thread_executor = ThreadPoolExecutor()

    def perform(self, playbook: Playbook) -> Any:
        action = self.get_action(playbook=playbook)
        if not action:
            raise ValueError(f"Action not found: {playbook.name}")

        args, kwargs = self.eval_args(args=playbook.args)

        result = action.perform(*args, executor=self, playbook=playbook, **kwargs)
        """
        if asyncio.iscoroutine(result):
            def _thread(coro):
                loop = _asyncio.ensure_event_loop()
                #loop = asyncio.get_running_loop()
                #print("run in thread: ", coro)
                #future = asyncio.run_coroutine_threadsafe(coro=coro, loop=loop)
                #return future.result()

                return loop.run_until_complete(coro)

            future = self._thread_executor.submit(_thread, coro=result)
            result = future.result()
        """
        self.extract_vars(data=result, vars=playbook.result)

        return result

    def get_action(self, playbook: Playbook) -> Union[Action, None]:
        if playbook is None or not isinstance(playbook, Playbook) or playbook.name is None:
            raise ValueError(f"Invalid playbook: {playbook}")

        action = self._action_loader.get(name=playbook.name)
        if action is None:
            action = loader.get(name=playbook.name)

        return action

    def _eval_var_with_attr(self, var):
        ss = var.split(".")
        o = self._variables.get(ss[0])
        if o is None:
            return None

        for s in ss[1:]:
            if isinstance(o, dict):
                o = o.get(s)
            else:
                o = getattr(o, s)
        return o

    def eval_vars(self, vars):
        if vars is None:
            return None
        elif isinstance(vars, str):
            if vars.startswith("$"):
                o = self._eval_var_with_attr(vars)
                if o is None:
                    return vars
                else:
                    return o
            else:
                return vars.format_map(SafeDict(self._variables))
        elif isinstance(vars, list):
            return [self.eval_vars(x) for x in vars]
        elif isinstance(vars, dict):
            evaled = {}
            for k, v in vars.items():
                evaled[self.eval_vars(k)] = self.eval_vars(v)
            return evaled
        else:
            return vars

    def eval_args(self, args: Union[str, List, Dict, None] = None) -> Tuple[List, Dict]:
        args_ = []
        kwargs = {}

        evaled_args = self.eval_vars(vars=args)

        if evaled_args is not None:
            if isinstance(evaled_args, list):
                args_ = evaled_args
            elif isinstance(evaled_args, dict):
                kwargs = evaled_args
            else:
                args_.append(evaled_args)

        return args_, kwargs

    def extract_vars(self, data, vars):
        if vars is None:
            pass
        elif isinstance(vars, str) and vars.strip().startswith("$"):
            self._variables[vars.strip()] = data
        elif isinstance(vars, list) and isinstance(data, list):
            for i in range(len(vars)):
                v = vars[i]
                if isinstance(v, str) and v.strip().startswith("$") and i < len(data):
                    v = v.strip()
                    self._variables[v] = data[i]
        elif isinstance(vars, dict) and isinstance(data, dict):
            for k, v in vars.items():
                if isinstance(k, str) and k.strip().startswith("$"):
                    k = k.strip()
                    self._variables[k] = data.get(v)

    @staticmethod
    def execute(playbook_file, variables={}) -> Any:
        playbook = Playbook.load(playbook_file)

        executor = PlaybookExecutor()
        executor.set_variable("__file__", playbook_file)

        if variables is not None:
            for k, v in variables.items():
                executor.set_variable(f"${k}", v)

        return executor.perform(playbook=playbook)
