import re
from datetime import datetime
from typing import List, Optional

from .._logging import get_logger
from ..actions import Action
from . import LLM, Message

_log = get_logger("LLM")


class Session:
    def __init__(self, llm: LLM, actions: Optional[List[Action]] = None) -> None:
        self._llm = llm
        self._actions = actions
        self._messages = []

    def add(self, message: Message):
        self._messages.append(message)

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def run(self, history: int = 5, rewrite: bool = False):
        if rewrite:
            self.rewrite(history=history)

        m = self._llm.chat(messages=self._messages[-1 * history:], functions=self._actions)
        if m.observations is not None:
            for om in m.observations:
                self.add(om)
        self.add(m)
        return m

    def react(self, history: int = 1, rewrite: bool = False, max_steps=5, log=False):
        """Ref : https://www.width.ai/post/react-prompting"""

        if rewrite:
            self.rewrite(history=history)

        primary_prompt = """
Solve a question answering task with interleaving Thought, Action, Observation steps.

Thought can reason about the current situation, and Action can be two types:
(1) Question[new question], which anwser the new question.
(2) Finish[answer], which returns the answer and finishes the task.

If need date and time info, it is: {datetime}

Output your thought and the next action.

Example:
```
Task: Who is Olivia Wilde's boyfriend? What is his current age raised to the 0.23 power?

Thought: I need to find out who Olivia Wilde's boyfriend is and then calculate his age raised to the 0.23 power.
Action: Question["Olivia Wilde boyfriend"]
Observation: Olivia Wilde started dating Harry Styles after ending her years-long engagement to Jason Sudeikis \
— see their relationship timeline.
Thought: I need to find out Harry Styles' age.
Action: Question["Harry Styles age"]
Observation: 29 years
Thought: I need to calculate 29 raised to the 0.23 power.
Action: Question[29^0.23]
Observation: 2.169459462491557

Thought: I now know the final answer.
Action: Finish["Harry Styles, Olivia Wilde's boyfriend, is 29 years old and his age raised to the 0.23 power is \
2.169459462491557."]
```

Task and Steps:
```
Task: {task}

{steps}
```

Your thought and the next Action:
        """
        if len(self._messages) < 1 and self._messages[-1].role != "user":
            return Message(role="assistant", content="Ask me a question.")

        messages = self._messages[-1 * history:]
        task = self.plain_messages(messages=messages, norole=True, nowrap=True)
        if log:
            _log.info(f"Task: {task}")

        steps = []
        finish = False
        anwser = Message(role="assistant", content="NOT ENOUGH INFO")
        for step in range(max_steps):
            instructions = primary_prompt.format(task=task, steps="\n".join(steps), datetime=datetime.now())

            m = self._llm.chat(messages=[Message(role="user", content=instructions)])

            content = m.content
            ss = content.split("\n")
            q_pattern = re.compile(r'Question\[(.*)\]')
            for s in ss:
                s = s.strip()
                steps.append(s)
                if log:
                    _log.info(f"{step} - {s}")
                if s.startswith("Action"):
                    if "Finish" in s:
                        finish = True
                        break
                    else:
                        questions = q_pattern.findall(s)
                        for q in questions:
                            m = self._llm.chat(messages=[Message(role="user", content=q)], functions=self._actions)
                            o_content = m.content.replace("\n", " ")
                            observation = f"Observation: {o_content}"
                            steps.append(observation)
                            if log:
                                _log.info(f"{step} - {observation}")
            if finish:
                break
        final_anwser_prompt = """
Please answer the final user question based on the following thought steps.

Thought Steps:
```
{steps}
```

Final question: {question}
Your Answer:
        """
        instructions = final_anwser_prompt.format(steps="\n".join(steps), question=task)
        anwser = self._llm.chat(messages=[Message(role="user", content=instructions)])
        self.add(anwser)
        return anwser

    def rewrite(self, history: int = 5):
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
        instructions = instructions.format(conversation=plain, question=self._messages[-1].content)

        m = self._llm.chat(messages=[Message(role="user", content=instructions)])
        self._messages[-1].content = m.content

    def plain_messages(self, messages: List[Message], norole=False, nowrap=False):
        plain = []
        for m in messages:
            role = "" if norole else f"{m.role}: "
            content = m.content if nowrap else m.content.replace("\n", "\\n")
            plain.append(f"{role}{content}")
        return "\n".join(plain)
