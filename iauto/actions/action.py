from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
                description=d.get("description") or ""
            )

            args = d.get("arguments")
            if args:
                func.arguments = []
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
                description=d["function"].get("description")
            )

            params = d.get("parameters")
            if params:
                func.arguments = []
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
        **kwargs
    ) -> Any:
        """
        Execute the action with the given arguments.

        Args:
            *args: Positional arguments for the action.
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
        **kwargs
    ) -> Any:
        """
        Execute the wrapped Python callable with the given arguments.

        Args:
            *args: Positional arguments for the callable.
            **kwargs: Keyword arguments for the callable.

        Returns:
            Any: The result of the callable execution.
        """
        return self._func(*args, **kwargs)


def create(func, spec: Dict) -> Action:
    """
    Factory function to create a FunctionAction.

    Args:
        func (Callable): The Python callable that the action will execute.
        spec (Dict): A dictionary representing the action's specification.

    Returns:
        Action: A FunctionAction instance with the given callable and specification.
    """
    return FunctionAction(func=func, spec=spec)
