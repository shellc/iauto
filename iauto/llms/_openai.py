import json
from typing import List, Optional

import openai

from ..actions import Action
from ._llm import LLM, ChatMessage, Message


class OpenAI(LLM):
    """"""

    def __init__(self, model: Optional[str] = None, **kwargs) -> None:
        super().__init__()
        self._model = model or "gpt-3.5-turbo"

        self._openai = openai.OpenAI(**kwargs)

    def generate(self, instructions: str, **kwargs) -> Message:
        if "model" not in kwargs:
            kwargs["model"] = self._model

        r = self._openai.completions.create(
            prompt=instructions,
            stream=False,
            **kwargs
        )
        return Message(content=r.choices[0].text)

    def chat(self, messages: List[ChatMessage] = [], functions: Optional[List[Action]] = None, **kwargs) -> ChatMessage:
        tools = None
        tool_choice = None
        if functions is not None:
            tools = []
            tool_choice = "auto"
            function_spec = [f.spec.openai_spec() for f in functions]
            tools.extend(function_spec)

        msgs = [{"role": m.role, "content": m.content} for m in messages]

        if "model" not in kwargs:
            kwargs["model"] = self._model

        r = self._openai.chat.completions.create(
            messages=msgs,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

        m = r.choices[0].message
        tool_calls = m.tool_calls
        if tool_calls and functions:
            available_function = dict(
                [(func.spec.name, func) for func in functions]
            )

            msgs.append(m)

            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_to_call = available_function[func_name]
                func_args = json.loads(tool_call.function.arguments)
                func_resp = None
                try:
                    func_resp = func_to_call(**func_args)
                except Exception as e:
                    print(f"Function call err: {e}, func_name={func_name}, args={func_args}, resp={func_resp}")
                    func_resp = str(e)
                    import traceback
                    traceback.print_exception(e)

                if func_resp is not None and not isinstance(func_resp, str):
                    try:
                        func_resp = json.dumps(func_resp or {}, ensure_ascii=False, indent=4)
                    except TypeError:
                        pass

                msgs.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": func_resp
                })

            r = self._openai.chat.completions.create(
                messages=msgs,
                **kwargs
            )
            m = r.choices[0].message
        return ChatMessage(role="assistant", content=m.content)
