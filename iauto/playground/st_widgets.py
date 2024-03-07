import json
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
    "agent": "Multi-agent"
}


def options(button_label, func):
    tab1, tab2 = st.tabs(["Design", "JSON"])

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
            "playbooks": [],
            "agents": []
        }
        st.session_state.llm_options = opts
    else:
        opts = st.session_state.llm_options

    # Set default values
    def _on_change(key):
        opts[key] = st.session_state[f"opts_{key}"]

    def _set_key(key, value):
        if key not in st.session_state:
            st.session_state[key] = value

    def _remove_all_keys():
        keys = list(st.session_state.keys())
        for k in keys:
            if k.startswith("opts_"):
                st.session_state.pop(k)

    def _set_dict_opts(key, d):
        for k, v in d.items():
            _set_key(f"opts_{key}_{k}", v)

    for k, v in opts.items():
        if k == "agents":
            for idx, agent in enumerate(v):
                _set_key(f"opts_agent_name_{idx}", agent["name"])
                _set_key(f"opts_agent_inst_{idx}", agent["instructions"])
                _set_key(f"opts_agent_desc_{idx}", agent["description"])
        elif isinstance(v, dict):
            _set_dict_opts(k, v)
        else:
            _set_key(f"opts_{k}", v)

    opts["mode"] = tab1.radio(
        "Mode",
        options=mode_options.keys(),
        format_func=lambda x: mode_options[x],
        key="opts_mode"
    )

    with tab1.expander("Multi-agent Options"):
        opts["agent_react"] = st.checkbox(
            "Enable ReAct",
            key="opts_agent_react",
            help="Agents react"
        )

        opts["instructions"] = st.text_area(
            "Instructions",
            placeholder="You are a usefull assistant.",
            key="opts_instructions",
            value=opts["instructions"]
        )

        st.markdown("Agents")

        opts["agent_nums"] = st.slider('Number of agents', min_value=1, max_value=5, key="opts_agent_nums")
        opts["agents"] = [None] * opts["agent_nums"]

        for idx in range(opts["agent_nums"]):
            st.text(f"# {idx+1}")
            name = st.text_input("Name", key=f"opts_agent_name_{idx}",
                                 placeholder="Role name", label_visibility="collapsed")
            inst = st.text_input(
                "Instructions",
                key=f"opts_agent_inst_{idx}",
                placeholder="For role instruction",
                label_visibility="collapsed"
            )
            desc = st.text_input(
                "Description",
                key=f"opts_agent_desc_{idx}",
                placeholder="For role selection",
                label_visibility="collapsed"
            )
            opts["agents"][idx] = {"name": name, "instructions": inst, "description": desc}

    provider_options = {
        "openai": ("OpenAI", "OpenAI compatible API"),
        "llama": ("Local", "GGUF models"),
    }

    opts["provider"] = tab1.radio(
        "LLM",
        options=provider_options.keys(),
        captions=[x[1] for x in provider_options.values()],
        format_func=lambda x: provider_options[x][0],
        key="opts_provider"
    )

    with tab1.expander("Options"):
        provider = opts["provider"]
        if provider == "openai":
            api_key = st.text_input(
                "API Key",
                value="$OPENAI_API_KEY",
                key="opts_oai_args_api_key"
            )
            opts["oai_args"]["api_key"] = api_key

            base_url = st.text_input(
                "API Base URL",
                value=os.environ.get("OPENAI_API_BASE") or None,
                key="opts_oai_args_base_url"
            )
            if base_url == "":
                base_url = None
            opts["oai_args"]["base_url"] = base_url

            model = st.text_input(
                "Model",
                value=os.environ.get("OPENAI_MODEL_NAME") or "gpt-3.5-turbo",
                key="opts_oai_args_model"
            )
            opts["oai_args"]["model"] = model
        elif provider == "llama":
            model = st.text_input(
                "Model path",
                value=os.environ.get("MODEL_PATH") or None,
                placeholder="GUUF model path",
                key="opts_llama_args_model_path"
            )
            opts["llama_args"]["model_path"] = model

            chat_format = st.text_input(
                "Chat format",
                placeholder="auto",
                value=os.environ.get("CHAT_FORMAT") or None,
                key="opts_llama_args_chat_format"
            )
            opts["llama_args"]["chat_format"] = chat_format

            repeat_penalty = st.number_input(
                "repeat_penalty",
                placeholder="",
                key="opts_chat_args_repeat_penalty"
            )

            if repeat_penalty:
                opts["chat_args"]["repeat_penalty"] = repeat_penalty

        if provider != "openai":
            top_k = st.number_input("top_k", value=2, key="opts_chat_args_top_k")
            opts["chat_args"]["top_k"] = top_k
        else:
            if "top_k" in opts["chat_args"]:
                opts["chat_args"].pop("top_k")

        temperature = st.number_input(
            "temperature",
            value=0.75,
            key="opts_chat_args_temperature"
        )
        opts["chat_args"]["temperature"] = temperature

    opts["use_tools"] = tab1.checkbox("Use tools", key="opts_use_tools")

    # Tools
    actions = utils.list_actions()
    options_action = [a.name for a in actions]
    opts["tools"] = tab1.multiselect(
        "Actions",
        options=options_action,
        placeholder="Select actions",
        key="opts_tools"
    )

    playbooks = utils.list_playbooks()
    options_playbook = dict(list(playbooks.keys()))

    llm_playbook_tools = tab1.multiselect(
        "Playbooks",
        options=options_playbook.keys(),
        format_func=lambda x: options_playbook[x],
        placeholder="Select playbooks",
        key="opts_playbooks"
    )
    opts["playbooks"] = llm_playbook_tools

    if tab1.button(label=button_label, type="primary", use_container_width=True):
        func(options=opts)
        st.rerun()

    opts_json = tab2.text_area(
        "JSON",
        label_visibility="collapsed",
        height=300,
        value=json.dumps(opts, indent=4, ensure_ascii=True)
    )
    if tab2.button("Load", key="load_json"):
        opts = json.loads(opts_json)
        st.session_state.llm_options = opts
        _remove_all_keys()
        st.rerun()

    return opts
