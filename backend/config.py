from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    mongodb_uri: str
    mongodb_db_name: str = "aarogyaaid"
    sambanova_api_key: str
    sambanova_base_url: str = "https://api.sambanova.ai/v1"
    sambanova_model: str = "Meta-Llama-3.3-70B-Instruct"
    cohere_api_key: str
    embedding_model: str = "embed-english-light-v3.0"
    admin_username: str = "admin"
    admin_password: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        env_file_encoding = "utf-8"

settings = Settings()