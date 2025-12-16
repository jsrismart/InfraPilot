from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "InfraPilot"
    ALLOW_ORIGINS: list[str] = ["*"]
    OLLAMA_MODEL: str = "qwen2.5-coder"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 300
    SKIP_TOOLS_BY_DEFAULT: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
