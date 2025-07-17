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
    @property
    def url(self) -> str:
        """Формирует URL для асинхронного подключения к PostgreSQL."""
        # Используем get_secret_value() для безопасного доступа к секрету
        return (
            f"postgresql+asyncpg://"
            f"{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class Settings(BaseSettings):
    """Основной класс настроек, объединяющий все остальные."""
    # model_config позволяет указать источник настроек - .env файл
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter='_' # Позволяет использовать BOT_TOKEN для settings.bot.token
    )

    bot: BotSettings
    db: DBSettings


# Создаем единственный экземпляр настроек, который будет использоваться во всем приложении
settings = Settings()