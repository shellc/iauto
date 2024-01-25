from abc import ABC, abstractmethod
from typing import List, Dict
from pydantic import BaseModel
from ..tools import Function


class Message(BaseModel):
    role: str
    content: str


class LLM(ABC):
    """LLM"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, instructions: str, functions: List[Function] = None, **kwargs) -> Message:
        """"""

    @abstractmethod
    def chat(self, messages: List[Message], functions: List[Function] = None, **kwargs) -> Message:
        """"""
