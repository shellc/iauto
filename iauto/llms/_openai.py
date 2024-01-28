import json
from typing import List

import openai

from ..actions import Action
from ._llm import LLM, Message


class OpenAI(LLM):
    """"""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self._openai = openai.OpenAI(**kwargs)

    def generate(self, instructions: str, functions: List[Action] = None, **kwargs) -> Message:
        messages = []
        messages.append(Message(
            role="user",
            content=instructions
        ))

        return self.chat(messages=messages, functions=functions, **kwargs)

    def chat(self, messages: List[Message] = [], functions: List[Action] = None, **kwargs) -> Message:
        tools = []
        if functions is not None:
            function_spec = [f.spec.openai_spec() for f in functions]
            tools.extend(function_spec)

        messages = [{"role": m.role, "content": m.content} for m in messages]

        r = self._openai.chat.completions.create(
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )

        m = r.choices[0].message
        tool_calls = m.tool_calls

        if tool_calls and functions:
            available_function = dict(
                [(func.spec.name, func) for func in functions]
            )

            messages.append(m)

            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_to_call = available_function[func_name]
                func_args = json.loads(tool_call.function.arguments)
                func_resp = None
                try:
                    func_resp = func_to_call(**func_args)
                except Exception as e:
                    func_resp = str(e)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": json.dumps(func_resp or {}, ensure_ascii=False)
                })
            r = self._openai.chat.completions.create(
                messages=messages,
                **kwargs
            )
            m = r.choices[0].message
        return Message(role="assistant", content=m.content)
