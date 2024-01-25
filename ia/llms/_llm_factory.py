from ._llm import LLM
from ._openai import OpenAI
from ._chatglm import ChatGLM


def create_llm(provider: str = "openai", **kwargs) -> LLM:
    if provider is None:
        provider = ''

    if provider.lower() == "openai":
        return OpenAI(**kwargs)
    elif provider.lower() == "chatglm":
        return ChatGLM(**kwargs)
    else:
        raise ValueError(f"Invalid LLM provider: {provider}")
