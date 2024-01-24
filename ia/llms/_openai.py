import json
from ._llm import LLM
from ..tools import get_function_descriptions
import openai


class OpenAI(LLM):
    """"""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self._openai = openai.OpenAI(**kwargs)

    def generate(self, instructions: str, functions=None, **kwargs) -> str:
        tools = []
        if functions is not None:
            function_descriptions = get_function_descriptions(functions=functions)
            tools.extend(function_descriptions)

        messages = [{
            "role": "user",
            "content": instructions
        }]

        r = self._openai.chat.completions.create(
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )

        m = r.choices[0].message
        tool_calls = m.tool_calls

        if tool_calls:
            available_function = dict(
                [(func.description()['name'], functions[name]) for name, func in functions.items()]
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
        return m.content
