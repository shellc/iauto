import copy
import json
from typing import Iterator, List, Optional, Union

import llama_cpp as llama
import llama_cpp.llama_types as llama_types

from ..._logging import get_logger

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
    messages.insert(0, {
        "role": "system",
        "content": "You're a useful assistant."
    })

    if tools is not None and len(tools) > 0:
        question = messages[-1]["content"]
        # conversations = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        tool_call_instruct = generate_function_instructions(functions=tools)
        system_message = f"""{tool_call_instruct}
Question: {question}
Thought: I need to think if I can give the final answer directly, \
if not I need to call the function to answer the question."""

        messages.append({"role": "system", "content": system_message})

    prompt = _format_raw_prompt(messages=messages)

    # if len(messages) > 0 and messages[-1]["role"] != "user":  # Completion
    #    prompt = prompt[:-len(f"{IM_END}\n{IM_START}assistant\n")]
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
    _log.debug(f"Resp: {resp}")

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

    """
    system_messages = []
    for m in messages:
        role = m['role']
        content = m["content"]
        if role in ["user", "assistant"]:
            prompt.append(f"{IM_START}{role}\n{content}{IM_END}")
        elif role == "system":
            system_messages.append(content)
    prompt.append(f"{IM_START}assistant\n")

    system = "You are a helpful assistant."
    if len(system_messages) > 0:
        system = "\n".join(system_messages).strip()
    system = f"{IM_START}system\n{system}{IM_END}"

    prompt.insert(0, system)
    """
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
    if all(m["role"] != 'user' for m in messages):
        raise ValueError('Invalid request: Expecting at least one user message.')

    messages = copy.deepcopy(messages)

    instruction = ''
    if functions:
        instruction = generate_function_instructions(functions=functions)

    messages_with_fncall = messages
    messages = []
    for m_idx, m in enumerate(messages_with_fncall):
        role, content, func_call = m["role"], m["content"], m.get("function_call")
        content = content or ''
        content = content.lstrip('\n').rstrip()
        if role == 'function':
            if (len(messages) == 0) or (messages[-1]["role"] != 'assistant'):
                raise ValueError(
                    'Invalid request: Expecting role assistant before role function.'
                )
            messages[-1]["content"] += f'\nObservation: {content}'
            if m_idx == len(messages_with_fncall) - 1:
                # add a prefix for text completion
                messages[-1]["content"] += '\nThought:'
        elif role == 'assistant':
            if len(messages) == 0:
                raise ValueError(
                    'Invalid request: Expecting role user before role assistant.'
                )
            if func_call is None:
                if functions:
                    content = f'Thought: I now know the final answer.\nFinal Answer: {content}'
            else:
                f_name, f_args = func_call['name'], func_call['arguments']
                if not content.startswith('Thought:'):
                    content = f'Thought: {content}'
                content = f'{content}\nAction: {f_name}\nAction Input: {f_args}'
            if messages[-1]["role"] == 'user':
                messages.append({
                    "role": "assistant",
                    "content": content.lstrip('\n').rstrip()
                })
            else:
                messages[-1]["content"] += '\n' + content
        elif role == "user":
            messages.append({
                "role": "user",
                "content": content.lstrip('\n').rstrip()
            })
        elif role == "system":
            instruction = content.lstrip('\n').rstrip() + instruction
        else:
            raise ValueError(f'Invalid request: Incorrect role {role}.')

    query = None
    if messages[-1]["role"] == "user":
        query = messages[-1]["content"]
        messages = messages[:-1]

    if len(messages) % 2 != 0:
        raise ValueError('Invalid request')

    history = []  # [(Q1, A1), (Q2, A2), ..., (Q_last_turn, A_last_turn)]
    for i in range(0, len(messages), 2):
        if messages[i]["role"] == 'user' and messages[i + 1]["role"] == 'assistant':
            usr_msg = messages[i]["content"].lstrip('\n').rstrip()
            bot_msg = messages[i + 1]["content"].lstrip('\n').rstrip()
            if instruction and (i == len(messages) - 2):
                usr_msg = f'{instruction}\n\nQuestion: {usr_msg}'
                instruction = ''
            history.append([usr_msg, bot_msg])
        else:
            raise ValueError(
                'Invalid request: Expecting exactly one user (or function) role before every assistant role.',
            )

    if instruction:
        assert query is not None
        query = f"{instruction}\n\nQuestion: {query}"

    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    if query:
        messages.append({"role": "user", "content": query})
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
