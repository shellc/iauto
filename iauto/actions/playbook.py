import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

try:
    from yaml import CLoader as yaml_loader
except ImportError:
    from yaml import Loader as yaml_loader

from yaml import load as yaml_load

from .action import ActionSpec

KEY_ARGS = "args"
KEY_ACTIONS = "actions"
KEY_RESULT = "result"
KEY_DESCRIPTION = "description"
KEY_SPEC = "spec"


class Playbook(BaseModel):
    """
    A class representing a playbook which includes a series of actions to be executed.

    Attributes:
        name (Optional[str]): The name of the playbook.
        description (Optional[str]): A brief description of what the playbook does.
        args (Union[str, List, Dict, None]): Arguments that can be passed to the actions in the playbook.
        actions (Optional[List['Playbook']]): A list of actions (playbooks) to be executed.
        result (Union[str, List, Dict, None]): The result of the playbook execution.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    args: Union[str, List, Dict, None] = None
    actions: Optional[List['Playbook']] = None
    result: Union[str, List, Dict, None] = None
    spec: Optional[ActionSpec] = None
    metadata: Dict[str, Any] = {}

    def resolve_path(self, path: str) -> str:
        """
        Resolves a potentially relative path to an absolute path using the playbook's metadata.

        Args:
            path (str): The file path that may be relative or absolute.

        Returns:
            str: The absolute path resolved from the given path and the playbook's metadata root.
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.metadata["__root__"], path)


def from_dict(d: Dict) -> Playbook:
    """
    Generate a Playbook object from the input dictionary.

    Attributes:
        d (Dict): The dictionary to convert into a Playbook object.

    Returns:
        playbook (Playbook): The converted Playbook object.
    """
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
        playbook.description = pb.get(KEY_DESCRIPTION)
        playbook.args = pb.get(KEY_ARGS)
        playbook.result = pb.get(KEY_RESULT)

        data_actions = pb.get(KEY_ACTIONS)
        if data_actions is not None:
            if not isinstance(data_actions, List):
                raise ValueError(f"Invalid actions: {data_actions}")

            actions = []
            for action in data_actions:
                action_pb = from_dict(action)
                actions.append(action_pb)

            playbook.actions = actions

        data_spec = pb.get(KEY_SPEC)
        if data_spec is not None:
            playbook.spec = ActionSpec.from_dict(data_spec)
    elif isinstance(pb, List):
        playbook.args = pb
    else:
        playbook.args = [pb]
    return playbook


def load(fname: str) -> Playbook:
    """Load a playbook from file.

    Attributes:
        fname (str): Path to the YAML file containing the playbook.

    Returns:
        playbook (Playbook): The loaded playbook.
    """
    with open(fname, 'r', encoding='utf-8') as f:
        data = yaml_load(f, Loader=yaml_loader)
        playbook = from_dict(data)
        root = os.path.dirname(fname)
        _resolve_path(playbook=playbook, root=root)

    return playbook


def _resolve_path(playbook: Playbook, root: str):
    if playbook.actions is not None and len(playbook.actions) > 0:
        for action in playbook.actions:
            action.metadata["__root__"] = root
            _resolve_path(action, root)
