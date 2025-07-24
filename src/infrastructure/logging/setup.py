import logging
import sys

def setup_logging():
    """
    Настраивает корневой логгер для вывода в stdout.
    Этот способ более надежен, чем basicConfig, и устойчив
    к переопределению сторонними библиотеками.
    """
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    
    # Устанавливаем уровень INFO. Все, что ниже (DEBUG), будет игнорироваться.
    root_logger.setLevel(logging.INFO)

    # Создаем обработчик, который будет выводить логи в консоль (stdout)
    handler = logging.StreamHandler(sys.stdout)
    
    # Создаем форматтер, чтобы логи были красивыми и информативными
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Добавляем обработчик к корневому логгеру.
    # Важно: сначала очищаем старые обработчики, если они есть.
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # "Канарейка": тестовое сообщение, чтобы убедиться, что наша настройка применилась
    logging.info("--- UNYIELDING LOGGING CONFIGURED ---")