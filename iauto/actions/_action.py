from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, List, Dict, Optional


class ActionArg(BaseModel):
    name: str
    type: str = "string"
    description: str
    required: bool = False


class ActionDef(BaseModel):
    name: str
    description: str
    arguments: Optional[List[ActionArg]]

    @staticmethod
    def from_dict(d: Dict) -> 'ActionDef':
        try:
            func = ActionDef(
                name=d.get("name"),
                description=d.get("description"),
                arguments=[]
            )

            args = d.get("arguments")
            if args:
                for arg in args:
                    func.arguments.append(ActionArg(**arg))
        except Exception as e:
            raise ValueError(f"Invalid ActionDef: {e}")
        return func

    def openai_function(self) -> Dict:
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
    @abstractmethod
    def definition(self) -> ActionDef:
        raise NotImplementedError()

    @abstractmethod
    def perform(self, **args: Any) -> Dict:
        raise NotImplementedError()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.perform(**kwargs)
