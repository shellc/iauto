from autogen import AssistantAgent, ConversableAgent
from typing_extensions import List, Optional

from ..actions._loader import register_action
from ..llms import ChatMessage, Session
from ._autogen_model_client import IASessionClient
from ._executor import AgentExecutor


@register_action(name="agents.create", spec={
    "description": "Create an agent."
})
def create_agent(
    *args,
    type: str = "assistant",
    session: Session,
    name: str = "assistant",
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    **kwargs
) -> ConversableAgent:
    if instructions is None:
        instructions = AssistantAgent.DEFAULT_SYSTEM_MESSAGE
    else:
        instructions += '\nReply "TERMINATE" in the end when everything is done.'

    llm_config = {
        "model": session.llm.model,
        "model_client_cls": "IASessionClient",
        "tools": []
    }

    if session.actions and len(session.actions) > 0:
        llm_config["tools"] = [a.spec.oai_spec() for a in session.actions]

    agent = None
    if type == "assistant":
        agent = AssistantAgent(
            name=name,
            system_message=instructions,
            description=description,
            llm_config=llm_config
        )
        agent.register_model_client(model_client_cls=IASessionClient, session=session)
    else:
        raise ValueError(f"Invalid agent type: {type}")
    return agent


@register_action(name="agents.executor", spec={
    "description": "Create a agent executor."
})
def create_agent_executor(
    *args,
    session: Session,
    agents: List[ConversableAgent],
    instructions: Optional[str] = None,
    max_consecutive_auto_reply: Optional[int] = 10,
    **kwargs
):
    return AgentExecutor(
        session=session,
        agents=agents,
        instructions=instructions,
        max_consecutive_auto_reply=max_consecutive_auto_reply
    )


@register_action(name="agents.run", spec={
    "description": "Submit a agent run."
})
def executor_run(
    *args,
    agent_executor: AgentExecutor,
    message: str,
    clear_history: Optional[bool] = True,
    silent: Optional[bool] = False,
    **kwargs
):
    m = agent_executor.run(
        message=ChatMessage(role="user", content=message),
        clear_history=clear_history,
        silent=silent
    )
    return m.get("summary", "")
