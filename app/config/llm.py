"""LLM factory for Orion."""

from langchain_core.language_models.chat_models import BaseChatModel

from app.config.settings import settings


SUPPORTED_PROVIDERS = ("vertexai", "gemini", "openai", "anthropic", "groq")


def get_llm() -> BaseChatModel:
    """Return the configured chat model for the active provider."""

    # TODO(Phase 1): implement the provider switch for Orion.
    # Supported providers:
    # - vertexai -> ChatVertexAI using Gemini on Vertex AI
    # - gemini -> ChatGoogleGenerativeAI (legacy direct Gemini API path)
    # - openai -> ChatOpenAI
    # - anthropic -> ChatAnthropic
    # - groq -> ChatGroq
    # Every provider should use settings.LLM_MODEL and temperature=0.
    # Raise a clear ValueError for unsupported providers.
    raise NotImplementedError("TODO: implement get_llm() in app/config/llm.py")
