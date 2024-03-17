import multiprocessing
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple, Union

from .action import Action
from .loader import ActionLoader
from .loader import loader as action_loader
from .playbook import (KEY_ACTIONS, KEY_ARGS, KEY_DESCRIPTION, KEY_RESULT,
                       Playbook)
from .playbook import load as playbook_load

VALID_KEYS = [KEY_ARGS, KEY_ACTIONS, KEY_RESULT, KEY_DESCRIPTION]


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


class Executor(ABC):
    """
    Abstract base class for an executor that can run playbooks.
    """

    def __init__(self) -> None:
        """
        Initializes the Executor.
        """
        super().__init__()
        self._variables = {}

    @abstractmethod
    def perform(self, playbook: Playbook) -> Any:
        """
        Execute the given playbook.

        Args:
            playbook (Playbook): The playbook to execute.

        Returns:
            Any: The result of the playbook execution.
        """

    @abstractmethod
    def get_action(self, playbook: Playbook) -> Union['Action', None]:
        """
        Retrieve the action associated with the given playbook.

        Args:
            playbook (Playbook): The playbook containing the action to retrieve.

        Returns:
            Union[Action, None]: The action to perform, or None if not found.
        """

    @abstractmethod
    def eval_args(self, args: Union[str, List, Dict, None] = None) -> Tuple[List, Dict]:
        """
        Evaluate the arguments passed to the playbook or action.

        Args:
            args (Union[str, List, Dict, None], optional): The arguments to evaluate.

        Returns:
            Tuple[List, Dict]: A tuple containing the evaluated arguments as a list or a dictionary.
        """

    @abstractmethod
    def extract_vars(self, data, vars):
        """
        Extract variables from the given data based on the vars specification.

        Args:
            data: The data from which to extract variables.
            vars: The specification of variables to extract from the data.
        """

    def set_variable(self, name: str, value: Any):
        """
        Set a variable in the executor's context.

        Args:
            name (str): The name of the variable to set.
            value (Any): The value to assign to the variable.
        """
        self._variables[name] = value

    @property
    def variables(self) -> Dict:
        """
        Get the current variables in the executor's context.

        Returns:
            Dict: A dictionary of the current variables.
        """
        return self._variables


class PlaybookExecutor(Executor):
    """
    Executes playbooks containing a sequence of actions.

    This executor handles the running of actions defined in a playbook, managing
    the necessary thread execution for asynchronous actions and the extraction
    and evaluation of variables from the results.
    """

    def __init__(self) -> None:
        """
        Initializes the PlaybookExecutor instance.

        Sets up an action loader to load actions and creates a thread executor for
        managing asynchronous action execution.
        """

        super().__init__()
        self._action_loader = ActionLoader()
        self._thread_executor = ThreadPoolExecutor()

    def perform(self, playbook: Playbook) -> Any:
        """
        Executes the given playbook.

        This method takes a Playbook object, retrieves the corresponding action,
        evaluates the arguments, and then performs the action. If the action's result
        is an asyncio coroutine, it is run in a separate thread. After the action is
        performed, any variables specified in the playbook's 'result' section are
        extracted and stored.

        Parameters:
        - playbook (Playbook): The playbook object containing the action to be executed.

        Returns:
        - Any: The result of executing the action in the playbook.

        Raises:
        - ValueError: If the action is not found or the playbook is invalid.
        """

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
            action = action_loader.get(name=playbook.name)

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
                o = getattr(o, s) if hasattr(o, s) else None
        return o

    def eval_vars(self, vars):
        """
        Evaluate the variables in the context of the current executor's state.

        This method takes a variable or a structure containing variables and
        evaluates them using the current state of variables stored within the
        executor. It supports strings, lists, and dictionaries. If a string
        variable starts with '$', it is treated as a reference to a variable
        which is then resolved. If the variable is not found, the string is
        returned as is. For lists and dictionaries, each element or key-value
        pair is recursively processed.

        Parameters:
        - vars (Union[str, List, Dict, None]): The variable or structure containing
            variables to be evaluated.

        Returns:
        - The evaluated variable, or the original structure with all contained
            variables evaluated.
        """

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
        """
        Evaluates and separates arguments into positional and keyword arguments.

        This method processes the input arguments, evaluating any variables within
        them using the current state of the executor. It then separates the evaluated
        arguments into positional (list) and keyword (dictionary) arguments.

        Parameters:
        - args (Union[str, List, Dict, None], optional): The arguments to evaluate and
            separate. Can be a string, list, dictionary, or None.

        Returns:
        - Tuple[List, Dict]: A tuple containing a list of positional arguments and a
            dictionary of keyword arguments.
        """

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
        """
        Extracts variables from the result data and stores them in the executor's state.

        This method takes the result data and the variables defined in the playbook's 'result'
        section, then stores these variables in the executor's state for later use. The method
        supports extracting variables from strings, lists, and dictionaries.

        Parameters:
        - data (Any): The result data from which variables will be extracted.
        - vars (Union[str, List, Dict, None]): The structure defining which variables to extract
            from the result data. It can be a string, a list, a dictionary, or None.

        If `vars` is a string that starts with '$', it is assumed to be a variable name, and the
        entire `data` is stored with that variable name. If `vars` is a list, each element in
        `vars` that starts with '$' is treated as a variable name, and the corresponding element
        in `data` is stored with that variable name, provided `data` is also a list and the indices
        match. If `vars` is a dictionary, each key that starts with '$' is treated as a variable
        name, and the value from `data` corresponding to the dictionary's value is stored with the
        variable name, provided `data` is also a dictionary and contains the keys.

        No action is taken if `vars` is None or if the data types of `vars` and `data` do not
        correspond as expected.
        """

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

    def resolve_path(self, path: str) -> str:
        """
        Resolves a given file path to an absolute path.

        If the given path is already an absolute path, it is returned unchanged.
        Otherwise, the path is resolved relative to the directory of the current
        playbook file, which is stored in the executor's variables under the key
        "__file__".

        Args:
            path (str): The file path to resolve.

        Returns:
            str: The resolved absolute file path.

        """
        if os.path.isabs(path):
            return path
        else:
            root = os.path.dirname(self.variables.get("__file__") or ".")
            if root is not None:
                return os.path.join(root, path)
            else:
                return path


def execute(playbook: Union[str, Playbook], variables={}) -> Any:
    """
    Executes a playbook from a given file with optional initial variables.

    This static method loads a playbook from the specified file, creates a new
    PlaybookExecutor instance, sets any initial variables, and then performs the
    playbook.

    Args:
        playbook_file (str): The path to the playbook file to be executed.
        variables (dict, optional): A dictionary of initial variables to set in
            the executor's context before executing the playbook. Defaults to an
            empty dictionary.

    Returns:
        Any: The result of executing the playbook, which could be of any type
        depending on the actions performed within the playbook.
    """

    playbook_fname = None
    if isinstance(playbook, str):
        playbook_fname = playbook
        playbook = playbook_load(playbook)

    executor = PlaybookExecutor()
    executor.set_variable("__file__", playbook_fname)

    variables = variables or {}
    variables.update(dict(os.environ))

    if variables is not None:
        for k, v in variables.items():
            executor.set_variable(f"${k}", v)

    return executor.perform(playbook=playbook)


_thread_executor = ThreadPoolExecutor()


def execute_in_thread(playbook, variables={}):
    kwargs = {
        "playbook": playbook,
        "variables": variables
    }
    future = _thread_executor.submit(execute, **kwargs)
    return future


def process_worker(queue, execute_kwargs):
    ret = execute(**execute_kwargs)
    queue.put(ret)


class ProcessFuture:
    def __init__(self, process, queue) -> None:
        self._process = process
        self._queue = queue

    def done(self):
        return not self._process.is_alive()

    def running(self):
        return self._process.is_alive()

    def result(self):
        return self._queue.get()


def execute_in_process(playbook, variables={}):
    queue = multiprocessing.Queue()
    kwargs = {
        "queue": queue,
        "execute_kwargs": {
            "playbook": playbook,
            "variables": variables
        }
    }
    process = multiprocessing.Process(target=process_worker, kwargs=kwargs)
    process.start()
    future = ProcessFuture(process=process, queue=queue)
    return future
