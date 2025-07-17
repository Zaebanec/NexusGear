from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from .env file.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Bot settings
    bot_token: str

    # Database settings
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    @property
    def database_url_asyncpg(self) -> str:
        """Generate async database URL for SQLAlchemy."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()