from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "aarogyaaid"
    sambanova_api_key: str = ""
    sambanova_base_url: str = "https://api.sambanova.ai/v1"
    sambanova_model: str = "Meta-Llama-3.3-70B-Instruct"
    gemini_api_key: str = ""
    embedding_model: str = "models/text-embedding-004"
    admin_username: str = "admin"
    admin_password: str = "changeme"
    jwt_secret: str = "changeme_secret"
    jwt_algorithm: str = "HS256"
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()