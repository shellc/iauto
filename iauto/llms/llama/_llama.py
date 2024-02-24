from typing import Iterator, List, Optional

import llama_cpp
from llama_cpp.llama_chat_format import LlamaChatCompletionHandlerRegistry

from ..._logging import get_logger
from ...actions import ActionSpec
from .._llm import LLM, ChatMessage, Function, Message, ToolCall
from ._qwen import qwen_chat_handler


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

        # kwargs["chat_handler"] = llama_cpp.llama_chat_format.functionary_chat_handler
        self._llm = llama_cpp.Llama(**kwargs)
        self._model = kwargs.get("model_path", "LLaMA")

        self._log = get_logger("LLaMA")

        if "qwen" in self._model.lower():
            self.register_qwen_fn()

    def generate(self, instructions: str, **kwargs) -> Message:
        """"""
        r = self._llm.create_completion(prompt=instructions, **kwargs)
        print(instructions)
        if isinstance(r, Iterator):
            raise ValueError(f"Invalid response: {r}")
        return Message(content=r["choices"][0]["text"])

    def chat(self, messages: List[ChatMessage] = [], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        tools_desciption = []
        tool_choice = "auto"

        if tools:
            tools_desciption = [t.oai_spec() for t in tools]

        msgs = [m.model_dump() for m in messages]
        r = self._llm.create_chat_completion(
            messages=msgs,
            tools=tools_desciption,
            tool_choice=tool_choice,
            **kwargs
        )

        m = r["choices"][0]["message"]

        resp = ChatMessage(role=m["role"], content=m["content"] or "")

        tool_calls = m.get("tool_calls")
        if tool_calls:
            resp.tool_calls = []
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_args = tool_call["function"]["arguments"]
                resp.tool_calls.append(
                    ToolCall(
                        id=tool_call["id"],
                        type=tool_call["type"],
                        function=Function(
                            name=func_name,
                            arguments=func_args
                        )
                    )
                )
        return resp

    @property
    def modle(self) -> str:
        return self._model

    def register_qwen_fn(self):
        REGISTER_FLAG = "llama_qwen_chat_handler_registered"
        if REGISTER_FLAG not in globals():
            registry = LlamaChatCompletionHandlerRegistry()
            registry.register_chat_completion_handler(name="qwen-fn", chat_handler=qwen_chat_handler, overwrite=True)
            globals()[REGISTER_FLAG] = True
