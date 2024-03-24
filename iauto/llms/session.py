import json
from datetime import datetime
from typing import Dict, List, Optional, Union

from ..actions import Action
from ..log import get_logger
from .llm import LLM, ChatMessage


class Session:
    """
    The Session class is responsible for managing a conversation with a language model (LLM).
    It handles the state of the conversation, including the messages exchanged and the actions
    that can be performed based on those messages.

    The Session class provides high-level methods to interact with a language model, allowing for
    complex conversation flows, tool integration, and message management.
    """

    def __init__(self, llm: LLM, actions: Optional[List[Action]] = None) -> None:
        """
        Initialize a new Session instance.

        Args:
            llm (LLM): An instance of a language model to be used for processing messages.
            actions (Optional[List[Action]]): A list of actions that can be performed
                within the session. Defaults to None, in which case no actions are set.

        Returns:
            None
        """
        self._log = get_logger("LLM")
        self._llm = llm
        self._actions = actions
        self._messages = []

    def add(self, message: ChatMessage) -> None:
        """
        Add a new ChatMessage to the session's message history.

        Args:
            message (ChatMessage): The message to add to the history.

        Returns:
            None
        """
        self._messages.append(message)

    @property
    def llm(self) -> LLM:
        """
        Get the language model (LLM) instance associated with the session.

        Returns:
            LLM: The language model instance used for processing messages.
        """
        return self._llm

    @property
    def messages(self) -> List[ChatMessage]:
        """
        Get the list of ChatMessage instances that represent the message history of the session.

        Returns:
            List[ChatMessage]: The list of messages exchanged during the session.
        """
        return self._messages

    @property
    def actions(self) -> Optional[List[Action]]:
        """
        Get the list of Action instances that can be performed within the session.

        Returns:
            Optional[List[Action]]: The list of actions available in the session, or an empty list if none are set.
        """
        return self._actions or []

    def _execute_tools(
        self,
        message: ChatMessage,
        history: List[ChatMessage],
        actions: List[Action],
        save_message: bool = True,
        **kwargs
    ) -> ChatMessage:
        if message.tool_calls is None or len(message.tool_calls) == 0:
            return message

        functions = dict([(func.spec.name.replace(".", "_"), func) for func in actions])

        if message.tool_calls and len(message.tool_calls) > 0:
            tool_call = message.tool_calls[0]
            if not tool_call.function:
                raise ValueError(f"Invalid function: {tool_call.function}")

            call_id = tool_call.id
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments or '{}'

            if func_name not in functions:
                # raise ValueError(f"Function not found: {func_name}")
                return message

            func_to_call = functions[func_name]

            func_resp = None
            try:
                func_args = json.loads(func_args)
                func_resp = func_to_call(**func_args)
            except Exception as e:
                self._log.warn(f"Function call err: {e}, func_name={func_name}, args={func_args}, resp={func_resp}")
                func_resp = str(e)

            if func_resp is not None and not isinstance(func_resp, str):
                try:
                    func_resp = json.dumps(func_resp or {}, ensure_ascii=False, indent=4)
                except TypeError:
                    self._log.warn("Function return values cannot be JSONized")

            if call_id is None:
                raise ValueError("tool_call_id required.")
            m = ChatMessage(
                role="tool",
                content=func_resp or f"{func_name} return nothing.",
                tool_call_id=call_id,
                name=func_name,
            )

            if save_message:
                self.add(message=message)
                self.add(message=m)

            return m
        else:
            return message

    def run(
        self,
        instructions: Optional[str] = None,
        messages: Optional[List[ChatMessage]] = None,
        history: int = 5,
        rewrite: bool = False,
        expect_json: int = 0,
        tools: Optional[List[Action]] = None,
        use_tools: bool = True,
        auto_exec_tools: bool = True,
        **kwargs
    ) -> Union[ChatMessage, Dict, List]:
        """
        Run a conversation flow based on provided instructions and messages, with the option to rewrite the input,
        expect a JSON response, and execute tools.

        Args:
            instructions (Optional[str]): Instructions to prepend to the messages before sending to the LLM as a system role message.
            messages (Optional[List[ChatMessage]]): A list of ChatMessage instances to include in the conversation.
                If not provided, the last 'history' number of messages from the session will be used.
            history (int): The number of recent messages from the session to consider in the conversation. Defaults to 5.
            rewrite (bool): Whether to rewrite the last user message to be clearer before running the session.
            expect_json (int): The number of times to attempt parsing the LLM's response as JSON before giving up.
            tools (Optional[List[Action]]): A list of Action instances representing tools that can be used in the session.
            use_tools (bool): Whether to include tool specifications when sending messages to the LLM.
            auto_exec_tools (bool): Automatically execute tools if they are called in the LLM's response.

        Returns:
            Union[ChatMessage, Dict]: The final ChatMessage from the LLM, or a dictionary if a JSON response is expected and successfully parsed.

        Raises:
            json.JSONDecodeError: If 'expect_json' is greater than 0 and the LLM's response cannot be parsed as JSON.
        """  # noqa: E501

        if rewrite:
            self.rewrite(history=history, **kwargs)

        if messages is None or len(messages) == 0:
            messages = self._messages[-1 * history:]
        if instructions is not None:
            messages.insert(0, ChatMessage(role="system", content=instructions))

        tools_spec = None
        if use_tools:
            if tools:
                tools_spec = [t.spec for t in tools]
            elif self._actions:
                tools_spec = [t.spec for t in self._actions]
        m = self._llm.chat(messages=messages, tools=tools_spec, **kwargs)
        if auto_exec_tools:
            m = self._execute_tools(message=m, history=messages, actions=tools or self._actions or [], **kwargs)

        if m.role == "tool":
            messages.extend(self._messages[-2:])
            m = self._llm.chat(messages=messages, **kwargs)

        json_obj = None
        if expect_json > 0:
            for i in range(expect_json):
                try:
                    json_obj = json.loads(m.content)
                    break
                except json.JSONDecodeError:
                    m = self._llm.chat(messages=messages, tools=tools_spec, **kwargs)
                    if auto_exec_tools:
                        m = self._execute_tools(
                            message=m,
                            history=messages,
                            actions=tools or self._actions or [],
                            **kwargs
                        )
            if json_obj is None:
                m.content = "{}"

        self.add(m)

        if json_obj:
            return json_obj
        else:
            return m

    def react(
        self,
        instructions: Optional[str] = None,
        messages: Optional[List[ChatMessage]] = None,
        history: int = 5,
        rewrite: bool = False,
        log: bool = False,
        max_steps: int = 3,
        tools: Optional[List[Action]] = None,
        use_tools: bool = True,
        auto_exec_tools: bool = True,
        **kwargs
    ) -> ChatMessage:
        """
        Perform a series of Thought, Action, and Observation steps to react to the user's last question and generate an answer.

        This method simulates a cognitive process by interleaving Thought (reasoning about the situation),
        Action (using tools to generate an observation or concluding the task), and Observation (result of the action).

        Args:
            instructions (Optional[str]): Additional instructions to provide context for the language model.
            messages (Optional[List[ChatMessage]]): The list of ChatMessage instances to include in the conversation.
                Defaults to the last 'history' messages if not provided.
            history (int): The number of recent messages from the session to consider. Defaults to 5.
            rewrite (bool): Whether to rewrite the last user message for clarity before processing. Defaults to False.
            log (bool): Whether to log the steps of the process. Defaults to False.
            max_steps (int): The maximum number of Thought/Action/Observation cycles to perform. Defaults to 3.
            tools (Optional[List[Action]]): A list of Action instances representing tools that can be used in the session.
            use_tools (bool): Whether to include tool specifications when sending messages to the LLM. Defaults to True.
            auto_exec_tools (bool): Whether to automatically execute tools if they are called in the LLM's response. Defaults to True.

        Returns:
            ChatMessage: The final ChatMessage containing the answer to the user's question or indicating that more information is needed.

        Raises:
            ValueError: If the provided messages list is empty or the last message is not from the user.
        """  # noqa: E501

        if messages is None or len(messages) == 0:
            messages = self._messages[-1 * history:]

        if len(messages) < 1 or messages[-1].role != "user":
            return ChatMessage(role="assistant", content="Ask me a question.")

        tools_spec = None
        if use_tools:
            if tools:
                tools_spec = [t.spec for t in tools]
            elif self._actions:
                tools_spec = [t.spec for t in self._actions]

        original_question = messages[-1].content
        question = original_question
        if rewrite:
            self.rewrite(history=history, **kwargs)
            question = messages[-1].content

        if instructions is None:
            instructions = ""

        react_prompt = """{instructions}
Solve a task with interleaving Thought, Action, Observation steps.

Thought can reason about the current situation.
Action is the decision to act, use available tools, functions, or APIs as needed.

Use the following format:

Task: the task you must solve
Thought: you should always think about what to do
Action: action you make to act or tools/functions/APIs to call
Action Input: parameters to tools/functions/APIs
Observation: the result of the action
Thought: I now know the final answer
Finished: the final answer to the task if the task solved

Refer to the conversation hisotry to help you understand the task.

Begin!

Task: {task}
"""

        messages.append(
            ChatMessage(
                role="user",
                content=react_prompt.format(
                    task=question,
                    instructions=instructions
                )
            )
        )

        THOUGHT = "Thought: "
        ACTION = "Action: "
        # ACTION_INPUT = "Action Input: "
        OBSERVATION = "Observation: "
        FINISHED = "Finished: "

        stop = None
        if tools_spec is not None:
            stop = [OBSERVATION]

        if log:
            self._log.info(f"Task: {question}")

        answer = ChatMessage(role="assistant", content="NOT ENOUGH INFO")

        steps_count = 0
        while steps_count < max_steps:
            m = self._llm.chat(
                messages=messages,
                tools=tools_spec,
                stop=stop,
                **kwargs
            )
            answer.content = m.content  # for default answer if answer not found

            messages.append(m)

            content = m.content

            z = content.rfind(FINISHED)
            if z >= 0:
                answer.content = content[z + len(FINISHED):]
                break

            # fix qwen function calling result
            if all([x not in content for x in [ACTION, THOUGHT]]):
                answer.content = content
                break

            # try to execute tools
            m_tool = self._execute_tools(
                message=m,
                history=messages,
                actions=tools or self._actions or [],
                save_message=False,
                **kwargs
            )

            if m_tool.role == "tool":
                m_tool.content = f"{OBSERVATION}{m_tool.content}"
                messages.append(m_tool)

            steps_count += 1

        answer.content = answer.content.strip()
        self.add(answer)
        return answer

    def rewrite(self, history: int = 5, **kwargs) -> None:
        """
        Rewrite the last user message in the session's message history to be clearer and more complete based on the context of the conversation.

        This method utilizes the language model to reformulate the user's question, considering the conversation history to provide a clearer version of the question.

        Args:
            history (int): The number of recent messages from the session to consider for context. Defaults to 5.

        Returns:
            None: The method updates the last user message in the session's message history in place.

        Raises:
            ValueError: If there are no messages or the last message is not from the user.
        """  # noqa: E501

        instructions = """
Rewrite the following user question into a clearer and more complete question based on the context of the conversation.

Conversation:
```
{conversation}
```

Question: {question}
Rewrite as:
        """

        if len(self._messages) < 1 or self._messages[-1].role != "user":
            return

        messages = self._messages[-1 * history:-1]
        plain = self.plain_messages(messages=messages)
        instructions = instructions.format(
            conversation=plain, question=self._messages[-1].content, datetime=datetime.now())

        m = self._llm.chat(messages=[ChatMessage(role="user", content=instructions)], **kwargs)
        self._messages[-1].content = m.content

    def plain_messages(self, messages: List[ChatMessage], norole: bool = False, nowrap: bool = False) -> str:
        """
        Convert a list of ChatMessage instances into a plain string representation.

        Args:
            messages (List[ChatMessage]): The list of ChatMessage instances to convert.
            norole (bool, optional): If True, the role of the message sender is omitted. Defaults to False.
            nowrap (bool, optional): If True, newlines in the message content are replaced with '\\n'. Defaults to False.

        Returns:
            str: A string representation of the messages, each message on a new line.
        """  # noqa: E501

        plain = []
        for m in messages:
            role = "" if norole else f"{m.role}: "
            content = m.content if not nowrap else m.content.replace("\n", "\\n")
            plain.append(f"{role}{content}")
        return "\n".join(plain)
