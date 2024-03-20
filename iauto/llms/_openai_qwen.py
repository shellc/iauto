from typing import List, Optional

from ..actions import ActionSpec
from . import _qwen
from .llm import ChatMessage, Function, ToolCall
from .openai import OpenAI


class QWen(OpenAI):
    def chat(self, messages: List[ChatMessage] = [], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        # Fix bug for qwen fastchat
        for m in messages:
            if m.role == "tool":
                m.role = "user"

            if m.tool_call_id:
                m.content += f"\ntool_call_id: {m.tool_call_id}"
                m.tool_call_id = None
            if m.tool_calls:
                m.content += f"\ntool_calls: {m.tool_calls}"
                m.tool_calls = None

        if tools is None or len(tools) == 0:
            return super().chat(messages, **kwargs)

        # tools call
        tools_description = [t.oai_spec() for t in tools]
        qe_messages = [m.model_dump() for m in messages]
        # qe_messages = _qwen.parse_messages(messages=qe_messages, functions=tools_description)
        func_prompt = _qwen.generate_function_instructions(functions=tools_description)
        qe_messages.insert(0, {"role": "system", "content": func_prompt})

        messages = [ChatMessage.from_dict(m) for m in qe_messages]

        m = super().chat(messages=messages, tools=tools, **kwargs)
        choice = _qwen.parse_response(m.content)

        if choice["finish_reason"] == "tool_calls":
            contents = []
            content = choice["message"]["content"]
            contents.append(f"{content}")

            m.tool_calls = []
            for tool_call in choice["message"]["tool_calls"]:
                try:
                    func_name = tool_call["function"]["name"]
                    func_args = tool_call["function"]["arguments"]
                    m.tool_calls.append(
                        ToolCall(
                            id=tool_call["id"],
                            type=tool_call["type"],
                            function=Function(
                                name=func_name,
                                arguments=func_args
                            )
                        )
                    )

                    contents.append(f"Action: {func_name}")
                    contents.append(f"Action Input: {func_args}")
                except Exception:
                    self._log.warn(f"ToolCall error: {tool_call}")

            m.content = "\n".join(contents)
        elif choice["finish_reason"] == "stop":
            m.content = choice["message"]["content"]
        return m

    def plain_messages(self, messages: List[ChatMessage], norole=False, nowrap=False):
        plain = []
        for m in messages:
            role = "" if norole else f"{m.role}: "
            content = m.content if not nowrap else m.content.replace("\n", "\\n")
            plain.append(f"{role}{content}")
        return "\n".join(plain)
