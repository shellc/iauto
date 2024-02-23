from typing import Dict, List, Optional, Union

from autogen import (Agent, ConversableAgent, GroupChat, GroupChatManager,
                     UserProxyAgent)

from ..llms import ChatMessage, Session
from ._autogen_model_client import IASessionClient


class AgentExecutor:
    def __init__(
        self,
        agents: List[ConversableAgent],
        session: Session,
        instructions: Optional[str] = None,
        human_input_mode: Optional[str] = "NEVER",
        max_consecutive_auto_reply: Optional[int] = 10
    ) -> None:
        self._session = session
        self._agents = agents
        self.human_input_mode = human_input_mode

        llm_config = {
            "model": session.llm.model,
            "model_client_cls": "IASessionClient"
        }

        def termination_func(x): return x.get("content", "").upper().find("TERMINATE") >= 0
        code_execution_config = {"executor": "ipython-embedded"}

        if instructions is None:
            instructions = 'Reply "TERMINATE" in the end when everything is done.'

        self._user_proxy = UserProxyAgent(
            name="UserProxy",
            system_message=instructions,
            is_termination_msg=termination_func,
            code_execution_config=code_execution_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            llm_config=llm_config
        )
        self._user_proxy.register_model_client(model_client_cls=IASessionClient, session=session)

        function_map = {}
        if self._session.actions:
            for func in self._session.actions:
                function_map[func.spec.name.replace(".", "_")] = func
        self._user_proxy.register_function(function_map)

        if len(self._agents) == 1:
            self._recipient = self._agents[0]
        elif len(self._agents) > 1:
            if len(function_map) > 0:
                tools_proxy = UserProxyAgent(
                    name="FunctionCaller",
                    description="An assistant can execute functions.",
                    system_message=instructions,
                    is_termination_msg=termination_func,
                    code_execution_config=code_execution_config,
                    human_input_mode="NEVER",
                    max_consecutive_auto_reply=max_consecutive_auto_reply,
                    llm_config=llm_config
                )
                tools_proxy.register_function(function_map=function_map)
                tools_proxy.register_model_client(model_client_cls=IASessionClient, session=session)
                self._agents.append(tools_proxy)

            speaker_selection_method = "round_robin" if len(self._agents) == 2 else "auto"
            groupchat = GroupChat(
                agents=self._agents,
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

    def run(
        self,
        message: ChatMessage,
        clear_history: Optional[bool] = True,
        silent: Optional[bool] = False,
        **kwargs
    ) -> Dict:
        result = self._user_proxy.initiate_chat(
            self._recipient,
            clear_history=clear_history,
            silent=silent,
            message=message.content,
            summary_method="reflection_with_llm"
        )
        # last_message = result.chat_history[-1]["content"]
        summary = result.summary
        if isinstance(summary, dict):
            summary = summary["content"]

        return {
            "history": result.chat_history,
            "summary": summary,
            "cost": result.cost
        }

    def reset(self):
        for agent in self._agents + [self._user_proxy, self._recipient]:
            agent.reset()

    def set_human_input_mode(self, mode):
        self.human_input_mode = mode
        for agent in [self._user_proxy, self._recipient]:
            agent.human_input_mode = mode

    def register_human_input_func(self, func):
        for agent in self._agents + [self._user_proxy, self._recipient]:
            agent.get_human_input = func

    def register_print_received(self, func):
        for agent in self._agents + [self._user_proxy, self._recipient]:
            receive_func = ReceiveFunc(agent, func)
            agent.receive = receive_func


class ReceiveFunc:
    def __init__(self, receiver, print_recieved) -> None:
        self._receiver = receiver
        self._receive_func = receiver.receive
        self._print_recieved = print_recieved

    def __call__(
        self,
        message: Union[Dict, str],
        sender: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False
    ):
        if not silent:
            self._print_recieved(message=message, sender=sender, receiver=self._receiver)
        self._receive_func(message=message, sender=sender, request_reply=request_reply, silent=silent)
