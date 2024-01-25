from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, List, Dict, Optional


class FunctionArgument(BaseModel):
    name: str
    type: str = "string"
    description: str
    required: bool = False


class FunctionDescription(BaseModel):
    name: str
    description: str
    arguments: Optional[List[FunctionArgument]]

    @staticmethod
    def from_dict(desc: Dict) -> 'FunctionDescription':
        try:
            func = FunctionDescription(
                name=desc.get("name"),
                description=desc.get("description"),
                arguments=[]
            )

            args = desc.get("arguments")
            for arg in args:
                func.arguments.append(FunctionArgument(**arg))
        except Exception as e:
            raise ValueError(f"Invalid FunctionDescription: {e}")
        return func

    def to_openai_style(self) -> Dict:
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


class Function(ABC, BaseModel):
    description: FunctionDescription

    @abstractmethod
    def call(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.call(*args, **kwds)
