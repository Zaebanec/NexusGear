# src/infrastructure/config.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

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
    @property
    def url(self) -> str:
        """Формирует URL для асинхронного подключения к PostgreSQL."""
        return (
            f"postgresql+asyncpg://"
            f"{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )

# --- НАЧАЛО ИЗМЕНЕНИЯ ---
class AppSettings(BaseSettings):
    """Настройки для веб-приложения (TWA, API)."""
    base_url: str
    secret_token: SecretStr
# --- КОНЕЦ ИЗМЕНЕНИЯ ---


class Settings(BaseSettings):
    """Основной класс настроек, объединяющий все остальные."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter='__' # Используем двойное подчеркивание для вложенности
    )

    bot: BotSettings
    db: DBSettings
    # --- НАЧАЛО ИЗМЕНЕНИЯ ---
    app: AppSettings
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---


# Создаем единственный экземпляр настроек
settings = Settings()