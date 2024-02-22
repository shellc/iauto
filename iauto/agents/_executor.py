from typing import List, Union

from autogen import (ConversableAgent, GroupChat, GroupChatManager,
                     UserProxyAgent)

from ..llms import ChatMessage, Session
from ._autogen_model_client import IASessionClient


class AgentExecutor:
    def __init__(
        self,
        agents: List[ConversableAgent],
        session: Session,
    ) -> None:
        self._session = session
        self._agents = agents

        llm_config = {
            "model": "IASessionClient",
            "model_client_cls": "IASessionClient"
        }

        def termination_func(x): return x.get("content", "").upper().find("TERMINATE") >= 0
        code_execution_config = {"executor": "ipython-embedded"}
        max_consecutive_auto_reply = 3

        self._user_proxy = UserProxyAgent(
            name="UserProxy",
            system_message='Reply "TERMINATE" in the end when everything is done.',
            is_termination_msg=termination_func,
            code_execution_config=code_execution_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            llm_config=llm_config
        )
        self._user_proxy.register_model_client(model_client_cls=IASessionClient, session=session)
        if self._session.actions:
            function_map = {}
            for func in self._session.actions:
                function_map[func.spec.name] = func
            self._user_proxy.register_function(function_map)

        if len(self._agents) == 1:
            self._recipient = self._agents[0]
        elif len(self._agents) > 1:
            speaker_selection_method = "round_robin" if len(self._agents) == 2 else "auto"
            groupchat = GroupChat(
                agents=agents + [self._user_proxy],
                messages=[],
                speaker_selection_method=speaker_selection_method
            )
            mgr = GroupChatManager(
                groupchat=groupchat,
                name="GroupChatManager",
                llm_config=llm_config,
                is_termination_msg=termination_func,
                code_execution_config=code_execution_config,
                max_consecutive_auto_reply=max_consecutive_auto_reply,
            )
            mgr.register_model_client(model_client_cls=IASessionClient, session=session)
            self._recipient = mgr
        else:
            raise ValueError("agents error")

    def run(self, message: ChatMessage, **kwargs) -> Union[ChatMessage, None]:
        result = self._user_proxy.initiate_chat(
            self._recipient,
            message=message.content,
            summary_method="reflection_with_llm"
        )
        # last_message = result.chat_history[-1]["content"]
        summary = result.summary
        if isinstance(summary, dict):
            summary = summary["content"]
        m = ChatMessage(role="assistant", content=summary)
        return m.content
