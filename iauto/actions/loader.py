import importlib
from typing import Dict, Union

from .action import Action, create


class ActionLoader:
    """Manages the registration and retrieval of action instances.

    This class provides a mechanism to register actions by name and retrieve them.
    It keeps an internal dictionary that maps action names to action instances.
    """

    def __init__(self) -> None:
        self._actions = {}

    def register(self, actions: Dict[str, Action]):
        """
        Registers a set of actions.

        Args:
            actions (Dict[str, Action]): A dictionary with action names as keys and
                Action instances as values to be registered.
        """
        self._actions.update(actions)

    def get(self, name) -> Union[Action, None]:
        """
        Retrieves an action instance by its name.

        Args:
            name (str): The name of the action to retrieve.

        Returns:
            Action or None: The action instance if found, otherwise None.
        """
        return self._actions.get(name)

    @property
    def actions(self):
        """Gets a list of all registered action instances.

        Returns:
            list: A list of Action instances.
        """
        return [a for a in self._actions.values()]

    def load(self, identifier):
        """
        Loads an action from a given identifier.

        The identifier is expected to be a string in the format 'package.module.ClassName', where 'package.module'
        is the full path to the module containing the class 'ClassName' that is the action to be loaded.

        Args:
            identifier (str): A dot-separated path representing the action to be loaded.

        Raises:
            ValueError: If the action name conflicts with an already registered action.
            ImportError: If the module cannot be imported.
            AttributeError: If the class cannot be found in the module.

        Returns:
            None
        """
        ss = identifier.split(".")
        pkg = importlib.import_module('.'.join(ss[:-1]))
        if pkg != '':
            action = getattr(pkg, ss[-1])()
            name = action.definition.name
            if name in self._actions:
                raise ValueError(f"Action name conflic: {name}")
            self._actions[name] = action


"""Create an instance of ActionLoader.

This instance will be used to register and retrieve actions. It maintains a dictionary of actions that can be accessed or modified.
"""  # noqa: E501
loader = ActionLoader()


def register(name: str, spec: Dict):
    """
    Registers a new action with the provided name and specification.

    Args:
        name (str): The unique name of the action to register.
        spec (Dict): A dictionary containing the action specification.

    Returns:
        The created action instance.

    Decorates:
        func: The function to be transformed into an action.

    Raises:
        ValueError: If an action with the given name already exists.
    """

    def decorator(func, *args, **kwargs):
        action = create(func=func, spec=spec)
        action.spec.name = name
        loader.register({name: action})
        return action
    return decorator
