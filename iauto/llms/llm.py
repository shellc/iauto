from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..actions import ActionSpec


class Function(BaseModel):
    """
    Represents a function call with optional arguments.

    Attributes:
        name (str): The name of the function being called.
        arguments (Optional[str]): The arguments to be passed to the function, if any.
    """
    name: str
    arguments: Optional[str] = None


class ToolCall(BaseModel):
    """
    Represents a call to a specific tool with an optional function call.

    Attributes:
        id (str): The unique identifier for the tool call.
        type (str): The type of the tool.
        function (Optional[Function]): An optional Function instance representing the function call associated with \
        the tool, if any.
    """

    id: str
    type: str
    function: Optional[Function] = None


class Message(BaseModel):
    content: str


class Usage(BaseModel):
    """
    Represents a token usage.

    Attributes:
        input_tokens (int): The number of tokens in the input message.
        output_tokens (int): The number of tokens in the generated response message.
    """
    input_tokens: int
    output_tokens: int


class ChatMessage(Message):
    """
    Represents a chat message with additional metadata and optional tool call information.

    Attributes:
        role (str): The role of the entity sending the message (e.g., "user", "system", "assistant").
        tool_calls (Optional[List[ToolCall]]): A list of ToolCall instances representing the tool calls associated \
        with this message, if any.
        tool_call_id (Optional[str]): The identifier of the tool call associated with this message, if any.
        name (Optional[str]): The name of the tool or function called.
        useage (Optional[Usage]): The token usage.
    """

    role: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    usage: Optional[Usage] = None

    @staticmethod
    def from_dict(d: Dict) -> "ChatMessage":
        """
        Create a ChatMessage instance from a dictionary.

        Parses the dictionary to populate the ChatMessage fields. If certain keys
        are not present in the dictionary, default values are used. For 'tool_calls',
        it creates a list of ToolCall instances from the sub-dictionaries.

        Args:
            d (Dict): The dictionary containing the ChatMessage data.

        Returns:
            ChatMessage: An instance of ChatMessage with properties populated from the dictionary.
        """

        m = ChatMessage(role="", content="")
        m.role = d.get("role") or ""
        m.content = d.get("content") or ""
        m.tool_call_id = d.get("tool_call_id")
        m.name = d.get("name")

        m.tool_calls = []
        tool_calls = d.get("tool_calls") or []
        for tool_call in tool_calls:
            m.tool_calls.append(
                ToolCall(
                    id=tool_call["id"],
                    type=tool_call["type"],
                    function=Function(
                        name=tool_call["function"]["name"],
                        arguments=tool_call["function"]["arguments"]
                    )
                )
            )
        return m


class LLM(ABC):
    """Abstract base class for a Language Model (LLM) that defines the interface for generating messages and handling \
    chat interactions."""

    def __init__(self) -> None:
        """Initialize the LLM instance."""
        super().__init__()

    @abstractmethod
    def generate(self, instructions: str, **kwargs) -> Message:
        """
        Generate a message based on the given instructions.

        Args:
            instructions (str): The instructions or prompt to generate the message from.
            **kwargs: Additional keyword arguments that the concrete implementation may use.

        Returns:
            Message: The generated message as a Message instance.
        """

    @abstractmethod
    def chat(self, messages: List[ChatMessage], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        """
        Conduct a chat interaction by processing a list of ChatMessage instances and optionally using tools.

        Args:
            messages (List[ChatMessage]): A list of ChatMessage instances representing the conversation history.
            tools (Optional[List[ActionSpec]]): An optional list of ActionSpec instances representing tools that can be used in the chat.
            **kwargs: Additional keyword arguments that the concrete implementation may use.

        Returns:
            ChatMessage: The response as a ChatMessage instance after processing the interaction.
        """  # noqa: E501

    @property
    @abstractmethod
    def model(self) -> str:
        """Abstract property that should return the model identifier for the LLM instance.

        Returns:
            str: The model identifier.
        """
