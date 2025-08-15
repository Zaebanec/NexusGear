# src/infrastructure/config.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Настройки для Telegram бота."""
    token: SecretStr


class DBSettings(BaseSettings):
    """Настройки для подключения к базе данных."""
    host: str
    port: int
    user: str
    password: SecretStr
    name: str

    @computed_field
    def url(self) -> str:
        """Формирует URL для асинхронного подключения к PostgreSQL."""
        return (
            f"postgresql+asyncpg://"
            f"{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class AppSettings(BaseSettings):
    """Настройки для веб-приложения (TWA, API)."""
    base_url: str
    secret_token: SecretStr

# --- НАЧАЛО ИЗМЕНЕНИЯ ---
class GeminiSettings(BaseSettings):
    """Настройки для Google Gemini API."""
    api_key: SecretStr
# --- КОНЕЦ ИЗМЕНЕНИЯ ---


class Settings(BaseSettings):
    """Основной класс настроек, объединяющий все остальные."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter='__'
    )

    bot: BotSettings
    db: DBSettings
    app: AppSettings
    # --- НАЧАЛО ИЗМЕНЕНИЯ ---
    gemini: GeminiSettings
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---


# Создаем единственный экземпляр настроек
settings = Settings()  # type: ignore[call-arg]