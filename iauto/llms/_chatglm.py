import json
from datetime import datetime
from typing import List, Optional

import chatglm_cpp

from .._logging import get_logger
from ..actions import Action
from ._llm import LLM, Message

_log = get_logger("ChatGLM")


class ChatGLM(LLM):
    def __init__(self, model_path) -> None:
        super().__init__()
        self._llm = chatglm_cpp.Pipeline(model_path=model_path)

    def generate(self, instructions: str, functions: Optional[List[Action]] = None, **kwargs) -> Message:
        """"""
        messages = []
        messages.append(Message(
            role="user",
            content=instructions
        ))

        return self.chat(messages=messages, functions=functions, **kwargs)

    def _function_call_retry(self, messages, retries=3):
        r = None
        for i in range(retries):
            r = self._llm.chat(messages=messages)
            if r.tool_calls is not None:
                for t in r.tool_calls:
                    if t.function.name is not None and t.function.name != "":
                        return r
                    else:
                        _log.warn(f"function_name is null, retry: {i + 1}")
        return r

    def chat(self, messages: List[Message] = [], functions: Optional[List[Action]] = None, **kwargs) -> Message:
        last_message = messages[-1] if len(messages) > 0 else None

        if functions is not None:
            function_spec = [f.spec.openai_spec() for f in functions]
            system_instructions = f"""
                Retrieve real-time information using the current datetime: {datetime.now()}

                Answer the following questions as best as you can. You have access to the following tools:\n
            """
            system_instructions += json.dumps(function_spec, ensure_ascii=False, indent=4)

            messages.insert(-1, Message(
                role="system",
                content=system_instructions
            ))

        chatglm_messages = []
        for m in messages:
            chatglm_messages.append(chatglm_cpp.ChatMessage(role=m.role, content=m.content))
        _log.debug(chatglm_messages)
        r = self._function_call_retry(messages=chatglm_messages)

        if not isinstance(r, chatglm_cpp.ChatMessage):
            raise ValueError(f"invalid message type: {r}, expected: ChatMessage")

        tool_calls = r.tool_calls
        observations = []

        if tool_calls and functions:
            available_function = dict(
                [(func.spec.name, func) for func in functions]
            )

            def tool_call(**kwargs):
                return kwargs

            for tc in tool_calls:
                func_name = tc.function.name
                if not func_name:
                    continue
                _log.debug(f"Function to call: {func_name}")
                func_to_call = available_function[func_name]

                func_resp = None
                func_args = None
                try:
                    func_args = eval(tc.function.arguments, dict(tool_call=tool_call))
                    func_resp = func_to_call(**func_args)
                except Exception as e:
                    _log.warn(f"Function call error: {e}, func={func_name}, args={func_args}", exc_info=e)

                if func_resp is not None and not isinstance(func_resp, str):
                    try:
                        func_resp = json.dumps(func_resp or {}, ensure_ascii=False, indent=4)
                    except TypeError:
                        _log.warn("Function call result is not jsonizable.")
                        func_resp = str(func_resp)

                if func_resp is not None:
                    chatglm_messages.append(chatglm_cpp.ChatMessage(
                        role="user",
                        content=func_resp
                    ))
                    observations.append(Message(
                        role="user",
                        content=func_resp
                    ))
            if last_message is not None:
                chatglm_messages.append(chatglm_cpp.ChatMessage(
                    role=last_message.role,
                    content=last_message.content
                ))
            _log.debug(chatglm_messages)
            r = self._llm.chat(messages=chatglm_messages)

            if not isinstance(r, chatglm_cpp.ChatMessage):
                raise ValueError(f"invalid message type: {r}, expected: ChatMessage")

        m = Message(role="assistant", content=r.content, observations=observations)
        _log.debug(f"Generated: {m}")

        return m
