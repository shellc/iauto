from .llm import LLM
from .openai import OpenAI


def create_llm(provider: str = "openai", **kwargs) -> LLM:
    """
    Create a language model instance based on the specified provider.

    This factory function supports creating instances of different language
    models by specifying a provider. Currently supported providers are 'openai',
    'llama', and 'chatglm'. Depending on the provider, additional keyword
    arguments may be required or optional.

    Parameters:
    - provider (str): The name of the provider for the LLM. Defaults to 'openai'.
    - **kwargs: Additional keyword arguments specific to the chosen LLM provider.

    Returns:
    - LLM: An instance of the specified language model.

    Raises:
    - ImportError: If the required module for the specified provider is not installed.
    - ValueError: If an invalid provider name is given.
    """

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
            from .chatglm import ChatGLM
            return ChatGLM(**kwargs)
        except ImportError as e:
            raise ImportError(
                "Could not create ChatGLM. "
                "Please install it with `pip install chatglm_cpp`."
            ) from e
    else:
        raise ValueError(f"Invalid LLM provider: {provider}")
