import copy
import json
from typing import Iterator, List, Optional, Union

import llama_cpp as llama
import llama_cpp.llama_types as llama_types

from ..._logging import DEBUG, get_logger

_log = get_logger(__name__)

IM_START = '<|im_start|>'
IM_END = '<|im_end|>'
END_OF_TEXT = "<|endoftext|>"

STOPS = [IM_END, END_OF_TEXT, "\n\n\n"]


# @register_chat_completion_handler("qwen-fn")
def qwen_chat_handler(
    llama: llama.Llama,
    messages: List[llama_types.ChatCompletionRequestMessage],
    functions: Optional[List[llama_types.ChatCompletionFunction]] = None,
    function_call: Optional[llama_types.ChatCompletionRequestFunctionCall] = None,
    tools: Optional[List[llama_types.ChatCompletionTool]] = None,
    tool_choice: Optional[llama_types.ChatCompletionToolChoiceOption] = None,
    temperature: float = 0.2,
    top_p: float = 0.95,
    top_k: int = 40,
    min_p: float = 0.05,
    typical_p: float = 1.0,
    stream: bool = False,
    stop: Optional[Union[str, List[str]]] = [],
    response_format: Optional[llama_types.ChatCompletionRequestResponseFormat] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    repeat_penalty: float = 1.1,
    tfs_z: float = 1.0,
    mirostat_mode: int = 0,
    mirostat_tau: float = 5.0,
    mirostat_eta: float = 0.1,
    model: Optional[str] = None,
    logits_processor: Optional[llama.LogitsProcessorList] = None,
    grammar: Optional[llama.LlamaGrammar] = None,
    **kwargs,  # type: ignore
) -> Union[llama_types.ChatCompletion, Iterator[llama_types.ChatCompletionChunk]]:
    if _log.isEnabledFor(DEBUG):
        _log.debug(f"Original Messages: {messages}")

    messages = parse_messages(messages=messages, functions=tools)

    if _log.isEnabledFor(DEBUG):
        _log.debug(f"Parsed Messages: {messages}")

    prompt = _format_raw_prompt(messages=messages)

    if len(messages) > 0 and messages[-1]["role"] == "assistant":  # Completion
        prompt = prompt[:-len(f"{IM_END}\n{IM_START}assistant\n")]

    if _log.isEnabledFor(DEBUG):
        _log.debug(f"Raw prompt: {prompt}")

    stop = STOPS[::]
    if tools:
        stop.append("Observation")
    resp = llama.create_completion(
        prompt=prompt,
        stop=stop,
        stream=False,
        grammar=grammar,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        min_p=min_p,
        typical_p=typical_p,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        repeat_penalty=repeat_penalty,
        tfs_z=tfs_z,
        mirostat_mode=mirostat_mode,
        mirostat_tau=mirostat_tau,
        mirostat_eta=mirostat_eta,
        model=model,
        logits_processor=logits_processor,
    )

    if isinstance(resp, Iterator):
        raise ValueError(f"Invalid resp: {resp}")

    content = resp["choices"][0]["text"].strip()
    if tools is not None:
        choice = parse_response(resp=content)
    else:
        choice = {
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop"
        }
    usage = resp.get("usage") or llama_types.CompletionUsage(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0
    )

    if _log.isEnabledFor(DEBUG):
        _log.debug(f"Resp: {resp}")

    return llama_types.CreateChatCompletionResponse(
        id="chat" + resp["id"],
        object="chat.completion",
        created=resp["created"],
        model=resp["model"],
        choices=[llama_types.ChatCompletionResponseChoice(**choice)],
        usage=usage,
    )


# https://github.com/QwenLM/Qwen/blob/main/openai_api.py
TOOL_DESC = (
    '`{name_for_model}`: Call this tool to interact with the {name_for_human} API.'
    ' What is the `{name_for_human}` API useful for? {description_for_model} Parameters: {parameters}'
)

REACT_INSTRUCTION = """Answer the following questions as best you can. You have access to the following APIs:

{tools_text}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tools_name_text}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!"""


def _format_raw_prompt(messages):
    prompt = []

    for m in messages:
        role = m['role']
        content = m["content"]
        prompt.append(f"{IM_START}{role}\n{content}{IM_END}")
    prompt.append(f"{IM_START}assistant\n")

    return "\n".join(prompt)


def generate_function_instructions(functions):
    tools_text = []
    tools_name_text = []

    for func_info in functions:
        type = func_info.get("type")
        if type != "function":
            continue
        else:
            func_info = func_info["function"]
        name = func_info.get('name', '')
        name_m = func_info.get('name_for_model', name)
        name_h = func_info.get('name_for_human', name)
        desc = func_info.get('description', '')
        desc_m = func_info.get('description_for_model', desc)
        tool = TOOL_DESC.format(
            name_for_model=name_m,
            name_for_human=name_h,
            # Hint: You can add the following format requirements in description:
            #   "Format the arguments as a JSON object."
            #   "Enclose the code within triple backticks (`) at the beginning and end of the code."
            description_for_model=desc_m,
            parameters=json.dumps(func_info['parameters'], ensure_ascii=False),
        )
        tools_text.append(tool)
        tools_name_text.append(name_m)
    tools_text = '\n\n'.join(tools_text)
    tools_name_text = ', '.join(tools_name_text)
    instruction = (REACT_INSTRUCTION.format(
        tools_text=tools_text,
        tools_name_text=tools_name_text,
    ).lstrip('\n').rstrip())

    return instruction


def parse_messages(messages, functions):
    if messages is None or len(messages) == 0:
        raise ValueError("Messages is empty.")

    if functions is None or len(functions) == 0:
        if all(m["role"] != "system" for m in messages):
            system = "You're a useful assistant."
            messages.insert(0, {"role": "system", "content": system})
        return messages

    # Function call
    instruction = generate_function_instructions(functions=functions)

    messages_with_fncall = copy.deepcopy(messages)
    messages = []
    for m_idx, m in enumerate(messages_with_fncall):
        role, content, tool_calls = m["role"], m["content"], m.get("tool_calls")
        content = content or ''
        content = content.lstrip('\n').rstrip()
        if role == 'tool':
            messages.append({
                "role": "tool",
                "content": f'\nObservation: {content}'
            })
        elif role == 'assistant':
            if tool_calls is None or len(tool_calls) == 0:
                if functions:
                    content = f'Thought: I now know the final answer.\nFinal Answer: {content}'
            else:
                f_name, f_args = tool_calls[0]["function"]['name'], tool_calls[0]["function"]['arguments']
                if not content.startswith('Thought:'):
                    content = f'Thought: {content}'
                content = f'{content}\nAction: {f_name}\nAction Input: {f_args}'
            if len(messages) > 0:
                if messages[-1]["role"] == 'user':
                    messages.append({
                        "role": "assistant",
                        "content": content.lstrip('\n').rstrip()
                    })
                elif messages[-1]["role"] == 'assistant':
                    messages[-1]["content"] += '\n' + content
            else:
                messages.append({
                    "role": "assistant",
                    "content": content.lstrip('\n').rstrip()
                })
        elif role == "user":
            messages.append({
                "role": "user",
                "content": f"Question: {content}"
            })
        elif role == "system":
            messages.append({"role": "system", "content": content})
        else:
            raise ValueError(f'Invalid request: Incorrect role {role}.')

    last = messages[-1]
    last_role = last["role"]
    query = last["content"].lstrip('\n').rstrip()
    messages = messages[:-1]

    # last_tool = messages[-1] if len(messages) > 0 and messages[-1]["role"] == "tool" else None
    last_user = None

    for m in messages[::-1]:
        role = m["role"]
        if last_user is None and role == "user":
            last_user = m
        if last_user:
            break

    if last_role == "tool":
        messages.append({
            "role": "user",
            "content": query
        })
    elif last_role == "user":
        messages.append({
            "role": "user",
            "content": f"{query}\nThought: "
        })
        """
        is_final_anwser = False
        if len(messages) > 0 and messages[-1]["role"] == "assistant" and "Final Answer" in messages[-1]["content"]:
            is_final_anwser = True

        if (last_tool and last_user) or (not is_final_anwser and last_user):
            user_content = last_user["content"].lstrip('\n').rstrip()
            last_user["content"] = f"{instruction}\n\nQuestion: {user_content}"

            content = f"Question: {query}\nThought: "
            messages.append({
                "role": "user",
                "content": content
            })
        else:
            messages.append({
                "role": "user",
                "content": f"{instruction}\n\nQuestion: {query}"
            })
            """
    elif last_role == "assistant":
        messages.append({
            "role": "assistant",
            "content": f"{query}\nThought: "
        })
    elif last_role == "system":
        messages.append({
            "role": "system",
            "content": query
        })
    else:
        raise ValueError(f"Invalid role: {last_role}")

    messages.insert(0, {
        "role": "system",
        "content": f"{instruction}\n\n{query}"
    })
    return messages


def parse_response(resp):
    func_name, func_args = '', ''
    if not resp.startswith("\n"):
        resp = "\n" + resp
    i = resp.find('\nAction:')
    j = resp.find('\nAction Input:')
    k = resp.find('\nObservation:')
    if 0 <= i < j:  # If the text has `Action` and `Action input`,
        if k < j:  # but does not contain `Observation`,
            # then it is likely that `Observation` is omitted by the LLM,
            # because the output text may have discarded the stop word.
            resp = resp.rstrip() + '\nObservation:'  # Add it back.
        k = resp.find('\nObservation:')
        func_name = resp[i + len('\nAction:'):j].strip()
        func_args = resp[j + len('\nAction Input:'):k].strip()

    if func_name:
        resp = resp[:i]
        t = resp.find('Thought: ')
        if t >= 0:
            resp = resp[t + len('Thought: '):]
        resp = resp.strip()

        choice = {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": resp,
                "function_call": {
                    "name": func_name,
                    "arguments": func_args,
                },
                "tool_calls": [
                    {
                        "id": func_name,
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "arguments": func_args,
                        },
                    }
                ],
            },
            "finish_reason": "tool_calls",
        }

        return choice

    z = resp.rfind('\nFinal Answer: ')
    if z >= 0:
        resp = resp[z + len('\nFinal Answer: '):]

    resp = resp.replace("Final", "").replace("Answer:", "").replace("Thought:", "")
    choice = {
        "index": 0,
        "message": {"role": "assistant", "content": resp.strip()},
        "finish_reason": "stop"
    }
    return choice
