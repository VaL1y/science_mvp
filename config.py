import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Science MVP")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "true").lower() == "true"

    DEFAULT_YEARS: int = int(os.getenv("DEFAULT_YEARS", 5))
    DEFAULT_LIMIT: int = int(os.getenv("DEFAULT_LIMIT", 200))


settings = Settings()
