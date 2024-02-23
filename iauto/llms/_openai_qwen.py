import json
from typing import List, Optional

from ..actions import ActionSpec
from ._llm import ChatMessage, Function, ToolCall
from ._openai import OpenAI
from .llama import _qwen


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
        instructions = []

        # conversations = self.plain_messages(messages=messages)
        # instructions.append(f"Conversation:\n```\n{conversations}\n```")

        tools_description = [t.oai_spec() for t in tools]

        instructions.append(_qwen.generate_function_instructions(functions=tools_description))

        if len(messages) == 0:
            raise ValueError("Message is empty.")

        last_message = messages[-1].content
        instructions.append(f"Question: {last_message}")

        instructions.append("Thought: I need to decide if I need to use a tool or function to answer the question.")

        messages.append(ChatMessage(role="system", content='\n'.join(instructions)))
        m = super().chat(messages=messages, tools=tools, **kwargs)

        choice = _qwen.parse_response(m.content)

        if choice["finish_reason"] == "tool_calls":
            m.tool_calls = []
            for tool_call in choice["message"]["tool_calls"]:
                try:
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
                except Exception:
                    self._log.warn(f"ToolCall error: {tool_call}")
            if len(m.tool_calls):
                m.content = json.dumps([tc.model_dump() for tc in m.tool_calls], ensure_ascii=False)
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
