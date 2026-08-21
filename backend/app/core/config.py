# WHAT DOES THIS FILE DO: Loads all env variables and sets up application configuration settings.

# ================== IMPORTS ==================
from pydantic_settings import BaseSettings, SettingsConfigDict
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Hold all the configs needed for running the FastAPI app.
class Settings(BaseSettings):
    """ Application settings container utilizing pydantic-settings. """

    # FLOW-1: Set up fields with correct types so pydantic can parse them.
    OPENAI_API_KEY: str                 # USE: For openai chat model connection
    TAVILY_API_KEY: str                 # USE: Tavily api token for web searching
    LANGSMITH_API_KEY: str              # USE: Token for langsmith tracing
    LANGSMITH_PROJECT: str              # USE: Name of project in langsmith
    DATABASE_URL: str                   # USE: Connection string for postgres db
    REDIS_URL: str                      # USE: Connection string for redis cache
    API_SECRET_KEY: str                 # USE: Secret token for api endpoints protection
    ENVIRONMENT: str = "development"    # USE: Current environment type
    LOG_LEVEL: str = "INFO"             # USE: App logging level default
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # USE: Allowed origins list for cors middleware
    CHROMA_PERSIST_PATH: str = "./chroma_db"  # USE: Local on-disk path for ChromaDB in development
    CHROMA_HOST: str | None = None      # USE: ChromaDB server host, set in production to use AsyncHttpClient
    CHROMA_PORT: int = 8000             # USE: ChromaDB server port, used only when CHROMA_HOST is set

    # FLOW-2: Config class to load from .env file directly.
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
# =========== CLASS ===========


# =========== VARIABLES : Application configuration singleton ===========
settings = Settings()           # USE: Global settings instance to import in other modules
# =========== VARIABLES : Application configuration singleton ===========