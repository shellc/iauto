from typing import List, Optional

import llama_cpp

from .._logging import get_logger
from ..actions import Action
from ._llm import LLM, Message

_log = get_logger("LLaMA")


class LLaMA(LLM):
    """
    llamap.cpp: https://github.com/ggerganov/llama.cpp
    llama-cpp-python: https://github.com/abetlen/llama-cpp-python
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()
        if "verbose" not in kwargs:
            kwargs["verbose"] = False

        if "n_ctx" not in kwargs:
            kwargs["n_ctx"] = 0

        if "n_gpu_layers" not in kwargs:
            kwargs["n_gpu_layers"] = -1

        self._llm = llama_cpp.Llama(**kwargs)

    def generate(self, instructions: str, functions: Optional[List[Action]] = None, **kwargs) -> Message:
        """"""
        messages = []
        messages.append(Message(
            role="user",
            content=instructions
        ))

        return self.chat(messages=messages, functions=functions, **kwargs)

    def chat(self, messages: List[Message] = [], functions: Optional[List[Action]] = None, **kwargs) -> Message:
        llama_messages = [m.model_dump() for m in messages]

        resp = self._llm.create_chat_completion(
            messages=llama_messages,
            **kwargs
        )

        m = Message(role="assistant", content=resp["choices"][0]["message"]["content"])
        _log.debug(f"Generated: {m}")

        return m
