"""Application settings for Orion."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings for the Orion application."""

    LLM_PROVIDER: str = "vertexai"
    LLM_MODEL: str = "gemini-2.5-flash"
    GOOGLE_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "orion"
    DATA_PATH: str = "data/sales_data.csv"
    PORT: int = 8080

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
