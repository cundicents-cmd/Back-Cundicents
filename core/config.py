from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Solo las variables que usa la app
    GEMINI_API_KEY: str
    GEMINI_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   
        case_sensitive=False
    )

settings = Settings()