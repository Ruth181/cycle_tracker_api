from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    google_client_id : str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_reasoning_effort: str | None = None
    llm_min_interval: float = 5

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()