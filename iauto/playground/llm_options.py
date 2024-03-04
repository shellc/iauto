import copy
import os

import streamlit as st

from . import utils


def render(button_label, func):
    options = None
    if "llm_options" not in st.session_state:
        options = {
            "llm_mode": (0, "chat", "Chat"),
            "llm_agent_react": False,
            "llm_provider": (0, "openai", "OpenAI"),
            "llm_args": {},
            "llm_chat_args": {},
            "llm_use_tools": False,
            "llm_playbook_as_tools": False,
            "llm_action_tools": [],
            "llm_playbook_tools": []
        }
    else:
        options = copy.deepcopy(st.session_state["llm_options"])

    llm_mode_options = {
        "chat": (0, "Chat"),
        "react": (1, "React"),
        "agent": (2, "Multi Agent")
    }

    llm_mode_key = st.radio(
        "Mode",
        options=llm_mode_options.keys(),
        index=options["llm_mode"][0],
        format_func=lambda x: llm_mode_options[x][1]
    )
    if llm_mode_key is not None:
        llm_mode = llm_mode_options[llm_mode_key]
        options["llm_mode"] = (llm_mode[0], llm_mode_key, llm_mode[1])

    if options["llm_mode"][0] == 2:
        options["llm_agent_react"] = st.checkbox(
            "Enable agents ReAct",
            value=options["llm_agent_react"]
        )

    llm_provider_options = {
        "openai": (0, "OpenAI", "OpenAI compatible API"),
        "llama": (1, "Local", "GGUF models"),
    }

    llm_provider_key = st.radio(
        "LLM",
        options=llm_provider_options.keys(),
        captions=[x[2] for x in llm_provider_options.values()],
        index=options["llm_provider"][0],
        format_func=lambda x: llm_provider_options[x][1]
    )
    if llm_provider_key:
        if llm_provider_key != options["llm_provider"][1]:
            options["llm_args"] = {}
        llm_provider = llm_provider_options[llm_provider_key]
        options["llm_provider"] = (llm_provider[0], llm_provider_key, llm_provider[1])

    with st.expander("Options"):
        llm_provider = options["llm_provider"][0]
        if llm_provider == 0:
            api_key = st.text_input(
                "API Key",
                value=options["llm_args"].get("api_key", os.environ.get("OPENAI_API_KEY") or "sk-")
            )
            options["llm_args"]["api_key"] = api_key

            base_url = st.text_input(
                "API Base URL",
                value=options["llm_args"].get("base_url", os.environ.get("OPENAI_API_BASE") or None)
            )
            if base_url == "":
                base_url = None
            options["llm_args"]["base_url"] = base_url

            model = st.text_input(
                "Model",
                value=options["llm_args"].get("model",  os.environ.get("OPENAI_MODEL_NAME") or "gpt-3.5-turbo")
            )
            options["llm_args"]["model"] = model
        elif llm_provider == 1:
            model = st.text_input(
                "Model path",
                value=options["llm_args"].get(
                    "model_path",
                    os.environ.get("MODEL_PATH") or "MODEL_PATH>"
                )
            )
            options["llm_args"]["model_path"] = model

            chat_format = st.text_input(
                "Chat format",
                placeholder="auto",
                value=options["llm_args"].get("chat_format", os.environ.get("LLAMA_CHAT_FORMAT"))
            )
            options["llm_args"]["chat_format"] = chat_format

            repeat_penalty = st.number_input(
                "repeat_penalty",
                value=options["llm_chat_args"].get("repeat_penalty", None)
            )

            if repeat_penalty:
                options["llm_chat_args"]["repeat_penalty"] = repeat_penalty

        if llm_provider != 0:
            top_k = st.number_input("top_k", value=options["llm_chat_args"].get("top_k", 2))
            options["llm_chat_args"]["top_k"] = top_k

        temperature = st.number_input(
            "temperature",
            value=options["llm_chat_args"].get("temperature", 0.75)
        )
        options["llm_chat_args"]["temperature"] = temperature

    options["llm_use_tools"] = st.checkbox("Use tools", value=options["llm_use_tools"])

    # Tools
    if options["llm_use_tools"]:
        actions = utils.list_actions()
        options_action = [a.name for a in actions]
        options["llm_action_tools"] = st.multiselect(
            "Actions",
            options=options_action,
            placeholder="Select actions",
            default=options["llm_action_tools"]
        )

        options["llm_playbook_as_tools"] = st.checkbox(
            "Playbook as tools",
            value=options["llm_playbook_as_tools"]
        )
        if options["llm_playbook_as_tools"]:
            playbooks = utils.list_playbooks()
            options_playbook = dict(list(playbooks.keys()))

            llm_playbook_tools = st.multiselect(
                "Playbooks",
                options=options_playbook.keys(),
                format_func=lambda x: options_playbook[x],
                placeholder="Select playbooks",
                default=options["llm_playbook_tools"]
            )
            options["llm_playbook_tools"] = llm_playbook_tools

    if st.button(label=button_label, type="primary"):
        st.session_state.llm_options = copy.deepcopy(options)
        func(options=options)
        st.rerun()
    return options
