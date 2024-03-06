import copy
import os
import uuid as _uuid

import streamlit as st

from . import utils

_namespace = _uuid.uuid1()


def uuid():
    return _uuid.uuid5(_namespace, _uuid.uuid1().hex).hex


mode_options = {
    "chat": "Chat",
    "react": "React",
    "agent": "Multi Agent"
}


def options(button_label, func):
    if "llm_options" not in st.session_state:
        opts = {
            "instructions": None,
            "mode": "chat",
            "agent_react": False,
            "provider": "openai",
            "oai_args": {},
            "llama_args": {},
            "chat_args": {},
            "use_tools": False,
            "tools": [],
            "playbook_as_tools": False,
            "playbooks": [],
            "agents": []
        }
        st.session_state.llm_options = opts
    else:
        opts = copy.deepcopy(st.session_state.llm_options)

    opts["mode"] = st.radio(
        "Mode",
        options=mode_options.keys(),
        format_func=lambda x: mode_options[x]
    )

    if opts["mode"] == "agent":
        opts["instructions"] = st.text_area("Instructions", height=30, placeholder="You are a usefull assistant.")

        st.markdown("Agents")

        agent_nums = st.slider('Number of agents', min_value=1, max_value=5)

        for idx in range(agent_nums):
            with st.expander(f"\\# {idx+1}"):
                name = st.text_input("Name", key=f"name_{idx}", placeholder="Role name")
                inst = st.text_input("Instructions", key=f"inst_{idx}", placeholder="For role instruction")
                desc = st.text_input("Description", key=f"desc_{idx}", placeholder="For role selection")
                opts["agents"].append({"name": name, "instructions": inst, "description": desc})

        opts["agent_react"] = st.checkbox(
            "Enable agents ReAct"
        )

    provider_options = {
        "openai": ("OpenAI", "OpenAI compatible API"),
        "llama": ("Local", "GGUF models"),
    }

    opts["provider"] = st.radio(
        "LLM",
        options=provider_options.keys(),
        captions=[x[1] for x in provider_options.values()],
        format_func=lambda x: provider_options[x][0]
    )

    with st.expander("Options"):
        provider = opts["provider"]
        if provider == "openai":
            api_key = st.text_input(
                "API Key",
                value=opts["oai_args"].get("api_key", "$OPENAI_API_KEY")
            )
            opts["oai_args"]["api_key"] = api_key

            base_url = st.text_input(
                "API Base URL",
                value=opts["oai_args"].get("base_url", os.environ.get("OPENAI_API_BASE") or None)
            )
            if base_url == "":
                base_url = None
            opts["oai_args"]["base_url"] = base_url

            model = st.text_input(
                "Model",
                value=opts["oai_args"].get("model",  os.environ.get("OPENAI_MODEL_NAME") or "gpt-3.5-turbo")
            )
            opts["oai_args"]["model"] = model
        elif provider == "llama":
            model = st.text_input(
                "Model path",
                value=opts["oai_args"].get(
                    "model_path",
                    os.environ.get("MODEL_PATH") or "MODEL_PATH>"
                )
            )
            opts["llama_args"]["model_path"] = model

            chat_format = st.text_input(
                "Chat format",
                placeholder="auto",
                value=opts["oai_args"].get("chat_format", os.environ.get("CHAT_FORMAT"))
            )
            opts["llama_args"]["chat_format"] = chat_format

            repeat_penalty = st.number_input(
                "repeat_penalty",
                value=opts["chat_args"].get("repeat_penalty", None)
            )

            if repeat_penalty:
                opts["chat_args"]["repeat_penalty"] = repeat_penalty

        if provider != "openai":
            top_k = st.number_input("top_k", value=opts["chat_args"].get("top_k", 2))
            opts["chat_args"]["top_k"] = top_k

        temperature = st.number_input(
            "temperature",
            value=opts["chat_args"].get("temperature", 0.75)
        )
        opts["chat_args"]["temperature"] = temperature

    opts["use_tools"] = st.checkbox("Use tools", value=opts["use_tools"])

    # Tools
    if opts["use_tools"]:
        actions = utils.list_actions()
        options_action = [a.name for a in actions]
        opts["tools"] = st.multiselect(
            "Actions",
            options=options_action,
            placeholder="Select actions",
            default=opts["tools"]
        )

        opts["playbook_as_tools"] = st.checkbox(
            "Playbook as tools",
            value=opts["playbook_as_tools"]
        )
        if opts["playbook_as_tools"]:
            playbooks = utils.list_playbooks()
            options_playbook = dict(list(playbooks.keys()))

            llm_playbook_tools = st.multiselect(
                "Playbooks",
                options=options_playbook.keys(),
                format_func=lambda x: options_playbook[x],
                placeholder="Select playbooks",
                default=opts["playbooks"]
            )
            opts["playbooks"] = llm_playbook_tools

    if st.button(label=button_label, type="primary", use_container_width=True):
        func(options=opts)
        st.rerun()

    return opts
