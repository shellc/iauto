from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

try:
    from yaml import CLoader as yaml_loader
except ImportError:
    from yaml import Loader as yaml_loader

from yaml import load


class Playbook(BaseModel):
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
    def __init__(self) -> None:
        super().__init__()
        self._variables = {}

    @abstractmethod
    def perform(self, playbook: Playbook) -> Any:
        """Eexcute playbook"""

    @abstractmethod
    def get_action(self, playbook: Playbook) -> Union['Action', None]:
        """"""

    @abstractmethod
    def eval_args(self, args: Union[str, List, Dict, None] = None) -> Tuple[List, Dict]:
        """"""

    @abstractmethod
    def extract_vars(self, data, vars):
        """"""

    def set_variable(self, name: str, value: Any):
        self._variables[name] = value

    @property
    def variables(self) -> Dict:
        return self._variables


class ActionArg(BaseModel):
    name: str
    type: str = "string"
    description: str
    required: bool = False


class ActionSpec(BaseModel):
    name: str
    description: str
    arguments: Optional[List[ActionArg]] = None

    @staticmethod
    def from_dict(d: Dict = {}) -> 'ActionSpec':
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
    def __init__(self) -> None:
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
        raise NotImplementedError()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.perform(*args, **kwargs)

    def copy(self):
        obj = type(self)()
        obj.spec = self.spec
        return obj


class FunctionAction(Action):
    def __init__(self, func, spec: Optional[Dict] = None) -> None:
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
        return self._func(*args, executor=executor, playbook=playbook, **kwargs)


def create_action(func, spec: Dict) -> Action:
    return FunctionAction(func=func, spec=spec)
