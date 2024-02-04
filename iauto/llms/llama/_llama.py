import json
from typing import Iterator, List, Optional

import llama_cpp

from ..._logging import get_logger
from ...actions import Action
from .._llm import LLM, ChatMessage, Message

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

        # kwargs["chat_handler"] = llama_cpp.llama_chat_format.functionary_chat_handler
        self._llm = llama_cpp.Llama(**kwargs)

    def generate(self, instructions: str, **kwargs) -> Message:
        """"""
        r = self._llm.create_completion(prompt=instructions, **kwargs)
        print(instructions)
        if isinstance(r, Iterator):
            raise ValueError(f"Invalid response: {r}")
        return Message(content=r["choices"][0]["text"])

    def chat(self, messages: List[ChatMessage] = [], functions: Optional[List[Action]] = None, **kwargs) -> ChatMessage:
        # last_message = messages[-1]

        tools = None
        tool_choice = None
        if functions is not None:
            tools = []
            tool_choice = "auto"
            function_spec = [f.spec.openai_spec() for f in functions]
            tools.extend(function_spec)

        msgs = [m.model_dump() for m in messages]
        r = self._llm.create_chat_completion(
            messages=msgs,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

        m = r["choices"][0]["message"]
        tool_calls = m.get("tool_calls")
        # observations = []
        if tool_calls and functions:
            available_function = dict(
                [(func.spec.name, func) for func in functions]
            )

            msgs.append(m)

            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_to_call = available_function.get(func_name)
                if func_to_call is None:
                    _log.warn(f"Function not found: {func_name}")
                    continue

                func_resp = None
                try:
                    func_args = json.loads(tool_call["function"]["arguments"])
                    func_resp = func_to_call(**func_args)
                except Exception as e:
                    print(f"Function call err: {e}, func_name={func_name}, args={func_args}, resp={func_resp}")
                    func_resp = str(e)

                if func_resp is not None and not isinstance(func_resp, str):
                    try:
                        func_resp = json.dumps(func_resp or {}, ensure_ascii=False, indent=4)
                    except TypeError:
                        pass

                msgs.append({
                    "tool_call_id": tool_call["id"],
                    "role": "function",
                    "name": func_name,
                    "content": func_resp
                })

                # observations.append(Message(
                #    role="function",
                #    content=func_resp
                # ))

                # if last_message is not None:
                #    msgs.append({
                #        "role": last_message.role,
                #        "content": last_message.content
                #    })
            r = self._llm.create_chat_completion(
                messages=msgs,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs
            )
            m = r["choices"][0]["message"]
        return ChatMessage(role="assistant", content=m["content"])
