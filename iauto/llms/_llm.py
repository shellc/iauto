from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..actions import ActionSpec


class Function(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    id: str
    type: str
    function: Optional[Function] = None


class Message(BaseModel):
    content: str


class ChatMessage(Message):
    role: str
    tool_calls: Optional[List[ToolCall]] = None


class LLM(ABC):
    """LLM"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, instructions: str, **kwargs) -> Message:
        """"""

    @abstractmethod
    def chat(self, messages: List[ChatMessage], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        """"""

    @property
    def model(self) -> str:
        ...
