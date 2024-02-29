from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

try:
    from yaml import CLoader as yaml_loader
except ImportError:
    from yaml import Loader as yaml_loader

from yaml import load


class Playbook(BaseModel):
    """
    A class representing a playbook which includes a series of actions to be executed.

    Attributes:
        name (Optional[str]): The name of the playbook.
        description (Optional[str]): A brief description of what the playbook does.
        args (Union[str, List, Dict, None]): Arguments that can be passed to the actions in the playbook.
        actions (Optional[List['Playbook']]): A list of actions (playbooks) to be executed.
        result (Union[str, List, Dict, None]): The result of the playbook execution.
        spec (Optional['ActionSpec']): The specification of the action that this playbook represents.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    args: Union[str, List, Dict, None] = None
    actions: Optional[List['Playbook']] = None
    result: Union[str, List, Dict, None] = None
    spec: Optional['ActionSpec'] = None

    @staticmethod
    def from_dict(d: Dict) -> 'Playbook':
        if d is None or len(d) != 1:
            raise ValueError(f"Invalid playbook: {d}")

        name = list(d.keys())[0]
        if name is None or not isinstance(name, str):
            raise ValueError(f"Invalid name: {name}")

        playbook = Playbook(
            name=name
        )

        pb = d[name]

        if isinstance(pb, Dict):
            playbook.description = pb.get("description")
            playbook.args = pb.get("args")
            playbook.result = pb.get("result")

            data_actions = pb.get("actions")
            if data_actions is not None:
                if not isinstance(data_actions, List):
                    raise ValueError(f"Invalid actions: {data_actions}")

                actions = []
                for action in data_actions:
                    action_pb = Playbook.from_dict(action)
                    actions.append(action_pb)

                playbook.actions = actions

            data_spec = pb.get("spec")
            if data_spec is not None:
                playbook.spec = ActionSpec.from_dict(data_spec)
        elif isinstance(pb, List):
            playbook.args = pb
        else:
            playbook.args = [pb]
        return playbook

    @staticmethod
    def load(fname: str) -> 'Playbook':
        with open(fname, 'r', encoding='utf-8') as f:
            data = load(f, Loader=yaml_loader)
            playbook = Playbook.from_dict(data)

        return playbook


class Executor(ABC):
    """
    Abstract base class for an executor that can run playbooks.

    Attributes:
        variables (Dict): A dictionary to hold variables that can be used in the execution context.
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


class ActionArg(BaseModel):
    """
    A class representing an argument for an action.

    Attributes:
        name (str): The name of the argument.
        type (str): The type of the argument, default is "string".
        description (str): A description of what the argument is for.
        required (bool): Whether the argument is required or optional, default is False.
    """
    name: str
    type: str = "string"
    description: str
    required: bool = False


class ActionSpec(BaseModel):
    """
    A class representing the specification of an action.

    Attributes:
        name (str): The name of the action.
        description (str): A brief description of what the action does.
        arguments (Optional[List[ActionArg]]): A list of arguments that the action accepts.
    """
    name: str
    description: str
    arguments: Optional[List[ActionArg]] = None

    @staticmethod
    def from_dict(d: Dict = {}) -> 'ActionSpec':
        """
        Create an ActionSpec instance from a dictionary representation.

        Args:
            d (Dict, optional): The dictionary containing action specification data.

        Returns:
            ActionSpec: An instance of ActionSpec created from the provided dictionary.

        Raises:
            ValueError: If the dictionary contains invalid data for creating an ActionSpec.
        """
        try:
            func = ActionSpec(
                name=d.get("name") or "UNNAMED",
                description=d.get("description") or "",
                arguments=[]
            )

            args = d.get("arguments")
            if args:
                for arg in args:
                    func.arguments.append(ActionArg(**arg))
        except Exception as e:
            raise ValueError(f"Invalid ActionDef: {e}")
        return func

    @staticmethod
    def from_oai_dict(d: Dict = {}) -> 'ActionSpec':
        """
        Create an ActionSpec instance from a dictionary following the OpenAPI Specification.

        Args:
            d (Dict, optional): The dictionary containing OpenAPI Specification data.

        Returns:
            ActionSpec: An instance of ActionSpec created from the provided OpenAPI dictionary.

        Raises:
            ValueError: If the dictionary does not conform to the expected OpenAPI Specification format.
        """
        try:
            if d["type"] != "function":
                raise ValueError(f"invalid function type: {d.get('type')}")
            func = ActionSpec(
                name=d["function"]["name"],
                description=d["function"].get("description"),
                arguments=[]
            )

            params = d.get("parameters")
            if params:
                for param in params["properties"].keys():
                    func.arguments.append(ActionArg(
                        name=param,
                        type=params["properties"][param]["type"],
                        description=params["properties"][param]["description"],
                        required=params["required"].get(params) is not None
                    ))
        except Exception as e:
            raise ValueError(f"Invalid ActionDef: {e}")
        return func

    def oai_spec(self) -> Dict:
        """
        Generate an OpenAPI Specification dictionary for this action.

        Returns:
            Dict: A dictionary representing the action in OpenAPI Specification format.
        """
        args = {}
        required = []

        if self.arguments:
            for arg in self.arguments:
                args[arg.name] = {
                    "type": arg.type,
                    "description": arg.description
                }
                if arg.required:
                    required.append(arg.name)

        return {
            "type": "function",
            "function": {
                "name": self.name.replace(".", "_"),
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": args,
                    "required": required
                }
            }
        }


class Action(ABC):
    """
    Abstract base class for an action.

    An action defines a single operation that can be performed. Actions are typically
    executed by an Executor within the context of a Playbook.

    Attributes:
        spec (ActionSpec): The specification of the action.
    """

    def __init__(self) -> None:
        """
        Initializes the Action.
        """
        super().__init__()
        self.spec = ActionSpec(name="UNNAMED", description="")

    @abstractmethod
    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        """
        Execute the action with the given arguments.

        Args:
            *args: Positional arguments for the action.
            executor (Optional[Executor]): The executor running this action.
            playbook (Optional[Playbook]): The playbook that this action is part of.
            **kwargs: Keyword arguments for the action.

        Returns:
            Any: The result of the action execution.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Allows the Action to be called as a function.

        Args:
            *args: Positional arguments for the action.
            **kwargs: Keyword arguments for the action.

        Returns:
            Any: The result of the action execution.
        """
        return self.perform(*args, **kwargs)

    def copy(self):
        """
        Create a copy of the Action instance.

        Returns:
            Action: A new instance of the Action with the same specification.
        """
        obj = type(self)()
        obj.spec = self.spec
        return obj


class FunctionAction(Action):
    """
    A concrete implementation of Action that wraps a Python callable.

    Attributes:
        _func (Callable): The Python callable to wrap.
        spec (ActionSpec): The specification of the action.
    """

    def __init__(self, func, spec: Optional[Dict] = None) -> None:
        """
        Initializes the FunctionAction with a Python callable and an optional specification.

        Args:
            func (Callable): The Python callable that this action will execute.
            spec (Optional[Dict]): A dictionary representing the action's specification.
        """
        super().__init__()
        self._func = func
        if spec:
            self.spec = ActionSpec.from_dict(spec)

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        """
        Execute the wrapped Python callable with the given arguments.

        Args:
            *args: Positional arguments for the callable.
            executor (Optional[Executor]): The executor running this action.
            playbook (Optional[Playbook]): The playbook that this action is part of.
            **kwargs: Keyword arguments for the callable.

        Returns:
            Any: The result of the callable execution.
        """
        return self._func(*args, executor=executor, playbook=playbook, **kwargs)


def create_action(func, spec: Dict) -> Action:
    """
    Factory function to create a FunctionAction.

    Args:
        func (Callable): The Python callable that the action will execute.
        spec (Dict): A dictionary representing the action's specification.

    Returns:
        Action: A FunctionAction instance with the given callable and specification.
    """
    return FunctionAction(func=func, spec=spec)
