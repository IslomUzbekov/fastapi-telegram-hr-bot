from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str

    internal_api_token: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    media_root: str = "media"

    @property
    def database_url(self) -> str:
        # psycopg2 URL
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
