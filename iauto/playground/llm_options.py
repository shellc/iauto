import os

import streamlit as st


def render():
    if "llm_args" not in st.session_state:
        st.session_state.llm_args = {}
    if "llm_chat_args" not in st.session_state:
        st.session_state.llm_chat_args = {}

    options = {
        "llm_provider": "openai",
        "llm_args": st.session_state["llm_args"],
        "llm_chat_args": st.session_state["llm_chat_args"]
    }

    llm_provider = st.radio(
        "LLM",
        ["OpenAI", "LLaMA", "ChatGLM"],
        captions=["OpenAI compatible API", "llama.cpp GGUF models", "chatglm.cpp GGUF model"],
    )

    options["llm_args"].clear()
    options["llm_chat_args"].clear()

    if llm_provider == "OpenAI":
        options["llm_provider"] = "openai"
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
    elif llm_provider == "LLaMA":
        options["llm_provider"] = "llama"

        model = st.text_input(
            "Model path",
            value=options["llm_args"].get(
                "llama_model_path", os.environ.get("LLAMA_MODEL_PATH") or "<LLAMA_MODEL_PATH>")
        )
        options["llm_args"]["model_path"] = model

        chat_format = st.text_input(
            "Chat format",
            placeholder="auto",
            value=options["llm_args"].get("chat_format", os.environ.get("LLAMA_CHAT_FORMAT"))
        )
        options["llm_args"]["chat_format"] = chat_format

        repeat_penalty = st.number_input(
            "repeat_penalty", value=options["llm_chat_args"].get("repeat_penalty", None))
        if repeat_penalty:
            options["llm_chat_args"]["repeat_penalty"] = repeat_penalty
    elif llm_provider == "ChatGLM":
        options["llm_provider"] = "chatglm"

        model = st.text_input(
            "Model path",
            value=options["llm_args"].get("model_path", os.environ.get(
                "CHATGLM_MODEL_PATH") or "<CHATGLM_MODEL_PATH>")
        )
        options["llm_args"]["model_path"] = model

    if llm_provider != "OpenAI":
        top_k = st.number_input("top_k", value=options["llm_chat_args"].get("top_k", 2))
        options["llm_chat_args"]["top_k"] = top_k

    temperature = st.number_input("temperature", value=options["llm_chat_args"].get("temperature", 0.75))
    options["llm_chat_args"]["temperature"] = temperature

    return options
