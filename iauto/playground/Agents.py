import json
import os
import tempfile

import streamlit as st

import iauto
from iauto.llms import ChatMessage
from iauto.playground import st_widgets, utils

try:
    from yaml import CDumper as yaml_dumper
except ImportError:
    from yaml import Dumper as yaml_dumper

from yaml import dump as yaml_dump

st.set_page_config(
    page_title='Agents',
    page_icon='🦾',
    layout='wide'
)

utils.logo()

here = os.path.dirname(__file__)
playbooks_dir = os.path.abspath(os.path.join(here, "playbooks"))

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

messages = st.session_state.messages

agent_executor = st.session_state.get("agent_executor")

# Initialize agent


def print_received(message, sender, receiver):
    content = ""
    if isinstance(message, str):
        content = message
    else:
        content = message["content"]
        if "tool_calls" in message:
            func_name = message["tool_calls"][0]["function"]["name"]
            func_args = message["tool_calls"][0]["function"]["arguments"]
            content = content + f"\nFunction call:\n```python\n{func_name}({func_args})\n```"

    message = f"**{sender.name}** (to {receiver.name})"
    json_obj = None
    content = content.strip()
    if content.startswith("{") or content.startswith("["):
        message = f"{message}\n\n```json\n{content}\n```"
        try:
            json_obj = json.loads(content)
        except Exception:
            pass
    else:
        message = f"{message}\n\n{content}"

    messages.append({"role": "assistant", "content": message, "json": json_obj})

    with st.chat_message("assistant"):
        st.markdown(message)
        if json_obj:
            st.json(json_obj, expanded=False)


def create_agent(options):
    reset()

    playbook = {
        "playbook": {
            "actions": [
                {
                    "llm.session": {
                        "args": {
                            "provider": options["provider"],
                            "llm_args": options["oai_args"] if options["provider"] == "openai" else options["llama_args"],  # noqa: E501
                            "tools": options["tools"]
                        },
                        "actions": [
                            {
                                "playbook": options["playbooks"]
                            }
                        ],
                        "result": "$llm_session"
                    }
                }
            ]
        }
    }

    agents = []
    agents_vars = []

    if len(options["agents"]) == 0:
        options["agents"].append({
            "name": "Assistant",
            "instructions": None,
            "description": None
        })
    for idx, agent in enumerate(options["agents"]):
        v = f"$agent_{idx}"
        agents.append({
            "agents.create": {
                "args": {
                    "session": "$llm_session",
                    "name": f"Assistant-{idx}" if agent["name"] == "" else agent["name"],
                    "instructions": agent["instructions"] if agent["instructions"] != "" else None,
                    "description": agent["description"] if agent["description"] != "" else None,
                    "react": options["agent_react"]
                },
                "result": v
            }
        })
        agents_vars.append(v)

    playbook["playbook"]["actions"].extend(agents)
    playbook["playbook"]["actions"].append({
        "agents.executor": {
            "args": {
                "session": "$llm_session",
                "instructions": options["instructions"],
                "react": options["agent_react"],
                "agents": agents_vars
            },
            "result": "$agent_executor"
        }
    })
    repl = {
        "repeat": {
            "actions": [
                {
                    "shell.prompt": {
                        "args": "Human: ",
                        "result": "$prompt"
                    }
                },
                {
                    "agents.run": {
                        "args": {
                            "agent_executor": "$agent_executor",
                            "message": "$prompt"
                        },
                        "result": "$message"
                    }
                },
                {
                    "shell.print": {
                        "args": {
                            "message": "AI: {$message}",
                            "color": "green"
                        }
                    }
                }
            ]
        }
    }

    playbook_yml = yaml_dump(
        playbook,
        Dumper=yaml_dumper,
        sort_keys=False,
        indent=2,
        allow_unicode=True,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=False
    ).strip()

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(playbook_yml.encode("utf-8"))
        f.close()

        agent_executor = iauto.execute(
            playbook=f.name
        )

        agent_executor.register_print_received(print_received)
        agent_executor.set_human_input_mode("NEVER")

    playbook["playbook"]["actions"].append(repl)
    playbook_yml = yaml_dump(
        playbook,
        Dumper=yaml_dumper,
        sort_keys=False,
        indent=2,
        allow_unicode=True,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=False
    ).strip()

    st.session_state.playbook_yml = playbook_yml
    st.session_state.agent_executor = agent_executor

    return playbook_yml, agent_executor


def clear():
    if agent_executor is not None:
        agent_executor.session.messages.clear()
        agent_executor.reset()
    messages.clear()


def reset():
    clear()
    st.session_state.agent_executor = None


def get_model():
    if agent_executor is not None:
        return agent_executor.session.llm.model


# Sidebar
with st.sidebar:
    button_label = "Reload" if agent_executor else "Launch"
    options = st_widgets.options(button_label=button_label, func=create_agent)

# Main container
# st.session_state
if "playbook_yml" in st.session_state:
    with st.expander("Generated playbook"):
        st.markdown(f"```yaml\n{st.session_state.playbook_yml}\n```")

if agent_executor:
    mode = options["mode"]
    mode_name = st_widgets.mode_options[mode]
    st.markdown(f"#### {mode_name}")

    if len(messages) == 0:
        greeting = "Hello! How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        with st.chat_message(role):
            if message["role"] == "user":
                content = f"{content}"
            st.markdown(content)
            if message.get("json"):
                st.json(message["json"], expanded=False)

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"{prompt}")

        agent_executor.session.add(ChatMessage(role="user", content=prompt))

        chat_args = options["chat_args"]
        use_tools = options["use_tools"]
        resp_message = None
        if mode == "chat":
            with st.spinner("Generating..."):
                resp = agent_executor.session.run(**chat_args, use_tools=use_tools)
                resp_message = resp.content
        elif mode == "react":
            with st.spinner("Reacting..."):
                resp = agent_executor.session.react(**chat_args, use_tools=use_tools)
                resp_message = resp.content
        elif mode == "agent":
            with st.status("Agents Conversation", expanded=True):
                resp = agent_executor.run(message=ChatMessage(role="user", content=prompt), clear_history=False)
                resp_message = resp["summary"]

        with st.chat_message("assistant"):
            st.markdown(resp_message)
            messages.append({"role": "assistant", "content": resp_message})

    if len(messages) > 1:
        st.button("Clear", type="secondary", help="Clear history", on_click=clear)

    model = get_model()
    st.markdown(f"```MODEL: {model}```")
else:
    st.warning("You need to launch a model first.")
