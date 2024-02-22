import json
import os
from typing import Iterator, List, Optional

import chatglm_cpp

from .._logging import DEBUG, get_logger
from ..actions import ActionSpec
from ._llm import LLM, ChatMessage, Function, Message, ToolCall


class ChatGLM(LLM):
    def __init__(self, model_path) -> None:
        super().__init__()
        if not os.path.isfile(model_path):
            raise ValueError(f"model_path must be a ggml file: {model_path}")
        self._llm = chatglm_cpp.Pipeline(model_path=model_path)

        self._log = get_logger("ChatGLM")

    def generate(self, instructions: str, **kwargs) -> Message:
        """"""
        text = self._llm.generate(prompt=instructions, stream=False, **kwargs)
        if not isinstance(text, str):
            raise ValueError("Invalid generated result.")
        return Message(content=text)

    def _function_call_retry(self, messages: List[chatglm_cpp.ChatMessage], retries=3, **kwargs):
        r = None
        for i in range(retries):
            r = self._llm.chat(messages=messages, stream=False, **kwargs)
            if isinstance(r, Iterator):
                raise ValueError(f"Invalid chat result: {r}")
            if r.tool_calls is not None:
                for t in r.tool_calls:
                    if t.function.name is not None and t.function.name != "":
                        return r
                    else:
                        self._log.warn(f"function_name is null, retry: {i + 1}")
        return r

    def chat(self, messages: List[ChatMessage] = [], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        use_tools = tools is not None and len(tools) > 0

        if use_tools:
            tools_desciption = [t.oai_spec() for t in tools]
            system_instructions = """
                Answer the following questions as best as you can. You have access to the following tools:\n
            """
            system_instructions += json.dumps(tools_desciption, ensure_ascii=False, indent=4)

            messages.insert(-1, ChatMessage(
                role="system",
                content=system_instructions
            ))

        chatglm_messages = []
        for m in messages:
            role = m.role
            if role == "tool":
                role = "user"
            chatglm_messages.append(chatglm_cpp.ChatMessage(role=role, content=m.content))
        if self._log.isEnabledFor(DEBUG):
            self._log.debug(chatglm_messages)
        if use_tools:
            r = self._function_call_retry(messages=chatglm_messages, **kwargs)
        else:
            r = self._llm.chat(messages=chatglm_messages, stream=False, **kwargs)

        if not isinstance(r, chatglm_cpp.ChatMessage):
            raise ValueError(f"invalid message type: {r}, expected: ChatMessage")

        resp = ChatMessage(role=r.role, content=r.content)

        tool_calls = r.tool_calls

        if tool_calls and use_tools:
            def tool_call(**kwargs):
                return kwargs

            resp.tool_calls = []

            for tc in tool_calls:
                func_name = tc.function.name
                if not func_name:
                    continue
                self._log.debug(f"Function to call: {func_name}")

                func_args = eval(tc.function.arguments, dict(tool_call=tool_call))

                resp.tool_calls.append(
                    ToolCall(
                        id=func_name,
                        type=tc.type,
                        function=Function(
                            name=func_name,
                            arguments=json.dumps(func_args, ensure_ascii=False)
                        )
                    )
                )
        return resp

    @property
    def modle(self) -> str:
        return "ChatGLM"
