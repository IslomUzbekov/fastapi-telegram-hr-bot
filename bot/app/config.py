from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    backend_url: str
    internal_api_token: str
    webapp_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
