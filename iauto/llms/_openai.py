import json
from typing import List, Optional

import openai

from .. import _logging
from ..actions import ActionSpec
from ._llm import LLM, ChatMessage, Function, Message, ToolCall


class OpenAI(LLM):
    """"""

    def __init__(self, model: Optional[str] = None, **kwargs) -> None:
        super().__init__()
        self._model = model or "gpt-3.5-turbo"

        self._openai = openai.OpenAI(**kwargs)

        self._log = _logging.get_logger("OpenAI")

    def generate(self, instructions: str, **kwargs) -> Message:
        if "model" not in kwargs:
            kwargs["model"] = self._model

        r = self._openai.completions.create(
            prompt=instructions,
            stream=False,
            **kwargs
        )
        return Message(content=r.choices[0].text)

    def chat(self, messages: List[ChatMessage] = [], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        if "model" not in kwargs:
            kwargs["model"] = self._model

        tools_desciption = None
        tool_choice = "auto"

        if tools:
            tools_desciption = [t.oai_spec() for t in tools]

        msgs = []
        for m in messages:
            msg = {
                "role": m.role,
                "content": m.content
            }
            if m.tool_call_id:
                msg["tool_call_id"] = m.tool_call_id
            if m.name:
                msg["name"] = m.name
            if m.tool_calls:
                msg["tool_calls"] = [t.model_dump() for t in m.tool_calls]
            msgs.append(msg)

        if self._log.isEnabledFor(_logging.DEBUG):
            self._log.debug(json.dumps({
                "messages": msgs,
                "tools": tools_desciption
            }, ensure_ascii=False, indent=4))

        if tools_desciption:
            kwargs["tools"] = tools_desciption
            kwargs["tool_choice"] = tool_choice

        r = self._openai.chat.completions.create(
            messages=msgs,
            **kwargs
        )

        m = r.choices[0].message

        resp = ChatMessage(role=m.role, content=m.content or "")

        tool_calls = m.tool_calls
        if tool_calls:
            resp.tool_calls = []
            for tool_call in tool_calls or []:
                func_name = tool_call.function.name
                func_args = tool_call.function.arguments
                resp.tool_calls.append(
                    ToolCall(
                        id=tool_call.id,
                        type=tool_call.type,
                        function=Function(
                            name=func_name,
                            arguments=func_args
                        )
                    )
                )

        return resp

    @property
    def model(self) -> str:
        return self._model
