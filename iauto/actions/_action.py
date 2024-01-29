from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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

    def openai_spec(self) -> Dict:
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
                "name": self.name,
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
    def perform(self, *args, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.perform(*args, **kwargs)


class FunctionAction(Action):
    def __init__(self, func, spec: Optional[Dict] = None) -> None:
        super().__init__()
        self._func = func
        if spec:
            self.spec = ActionSpec.from_dict(spec)

    def perform(self, *args, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)


def create_action(func, spec: Dict) -> Action:
    return FunctionAction(func=func, spec=spec)
