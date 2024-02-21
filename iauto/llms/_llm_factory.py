from ._llm import LLM
from ._openai import OpenAI


def create_llm(provider: str = "openai", **kwargs) -> LLM:
    if provider is None:
        provider = ''

    if provider.lower() == "openai":
        if kwargs.get("model", "").lower().find("qwen") >= 0:
            from ._openai_qwen import QWen
            return QWen(**kwargs)
        return OpenAI(**kwargs)
    elif provider.lower() == "llama":
        try:
            from .llama import LLaMA
            return LLaMA(**kwargs)
        except ImportError as e:
            raise ImportError(
                "Could not create LLaMA. "
                "Please install it with `pip install llama-cpp-python`."
            ) from e
    elif provider.lower() == "chatglm":
        try:
            from ._chatglm import ChatGLM
            return ChatGLM(**kwargs)
        except ImportError as e:
            raise ImportError(
                "Could not create ChatGLM. "
                "Please install it with `pip install chatglm_cpp`."
            ) from e
    else:
        raise ValueError(f"Invalid LLM provider: {provider}")
