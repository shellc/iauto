from autogen import AssistantAgent, ConversableAgent
from typing_extensions import Dict, List, Optional

from ..actions.loader import register
from ..llms import ChatMessage, Session
from .executor import AgentExecutor
from .model_clients import SessionClient


@register(name="agents.create", spec={
    "description": "Create a new agent instance.",
    "arguments": [
        {
            "name": "type",
            "description": "The type of agent to create.",
            "type": "string",
            "default": "assistant",
            "enum": ["assistant"]
        },
        {
            "name": "session",
            "description": "The LLM Session instance containing the state and configuration.",
            "type": "Session"
        },
        {
            "name": "llm_args",
            "description": "Additional arguments for the language model.",
            "type": "dict",
            "required": False
        },
        {
            "name": "react",
            "description": "Whether the agent should use react reasning.",
            "type": "bool",
            "required": False,
            "default": False
        },
        {
            "name": "name",
            "description": "The name of the agent.",
            "type": "string",
            "default": "assistant"
        },
        {
            "name": "description",
            "description": "A brief description of the agent's purpose.",
            "type": "string",
            "required": False
        },
        {
            "name": "instructions",
            "description": "Instructions for the agent.",
            "type": "string",
            "required": False
        }
    ]
})
def create_agent(
    *args,
    type: str = "assistant",
    session: Session,
    llm_args: Optional[Dict] = None,
    react: Optional[bool] = False,
    name: str = "assistant",
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    **kwargs
) -> ConversableAgent:
    if instructions is None or instructions == "":
        instructions = AssistantAgent.DEFAULT_SYSTEM_MESSAGE
    else:
        instructions += '\nReply "TERMINATE" in the end when everything is done.'

    if description is not None and description.strip() == "":
        description = None

    llm_config = {
        "model": session.llm.model,
        "model_client_cls": "SessionClient",
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
        agent.register_model_client(
            model_client_cls=SessionClient,
            session=session,
            react=react,
            llm_args=llm_args
        )
    else:
        raise ValueError(f"Invalid agent type: {type}")
    return agent


@register(name="agents.executor", spec={
    "description": "Instantiate a new agent executor.",
    "arguments": [
        {
            "name": "session",
            "description": "The LLM Session instance containing the state and configuration.",
            "type": "Session"
        },
        {
            "name": "llm_args",
            "description": "Additional arguments for the language model.",
            "type": "dict",
            "required": False
        },
        {
            "name": "react",
            "description": "Whether the agent should use react reasoning.",
            "type": "bool",
            "required": False,
            "default": False
        },
        {
            "name": "agents",
            "description": "A list of ConversableAgent instances to be managed by the executor.",
            "type": "List[ConversableAgent]"
        },
        {
            "name": "instructions",
            "description": "Instructions for the agent executor.",
            "type": "string",
            "required": False
        },
        {
            "name": "max_consecutive_auto_reply",
            "description": "The maximum number of consecutive auto-replies allowed by the executor.",
            "type": "int",
            "required": False,
            "default": 10
        }
    ]
})
def create_agent_executor(
    *args,
    session: Session,
    llm_args: Optional[Dict] = None,
    react: Optional[bool] = False,
    agents: List[ConversableAgent],
    instructions: Optional[str] = None,
    max_consecutive_auto_reply: Optional[int] = 10,
    **kwargs
):
    return AgentExecutor(
        session=session,
        llm_args=llm_args,
        react=react,
        agents=agents,
        instructions=instructions,
        max_consecutive_auto_reply=max_consecutive_auto_reply
    )


@register(name="agents.run", spec={
    "description": "Run the specified agent executor with a given message.",
    "arguments": [
        {
            "name": "agent_executor",
            "description": "The agent executor instance to run.",
            "type": "AgentExecutor"
        },
        {
            "name": "message",
            "description": "The message to process.",
            "type": "string"
        },
        {
            "name": "clear_history",
            "description": "Whether to clear the conversation history before running.",
            "type": "bool",
            "required": False,
            "default": True
        },
        {
            "name": "silent",
            "description": "Whether to suppress output during execution.",
            "type": "bool",
            "required": False,
            "default": False
        }
    ]
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
