from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings.

    Values are loaded from environment variables, falling back to a
    local .env file if present, and finally to the default values
    defined below if neither is set.
    """

    app_name: str = "Enterprise Dynamic Pricing Intelligence Platform API"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()