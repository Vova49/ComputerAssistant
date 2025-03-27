"""
Модуль для управления языками и командами в голосовом ассистенте.
Содержит словари команд для разных языков и функции перевода.
"""

# Команды на русском языке
RU_COMMANDS = {
    "TIMER_COMMANDS": ["включи таймер", "поставь таймер", "засеки", "запусти таймер", "таймер на"],
    "CLOSE_ALL_TIMERS_COMMANDS": ["закрой все таймеры", "выключи все таймеры", "закрой все таймер",
                                  "выключи все таймер", "стоп все таймеры", "стоп все таймер"],
    "TIME_COMMANDS": ["скажи время", "какое время", "который час", "сколько времени"],
    "WEATHER_COMMANDS": ["погода", "какая погода", "сейчас тепло", "сколько градусов", "какая температура"],
    "RADIO_ON_COMMANDS": ["включи радио", "открой радио"],
    "RADIO_OFF_COMMANDS": ["выключи радио", "закрой радио"],
    "GREETING_COMMANDS": ["привет"],
    "THANKS_COMMANDS": ["спасибо", "благодарю"],
    "SHUTDOWN_COMMANDS": ["выключи компьютер"],
    "MUSIC_ON_COMMANDS": ["включи музыку"],
    "MUSIC_OFF_COMMANDS": ["выключи музыку"],
    "CALCULATOR_COMMANDS": ["открой калькулятор", "включи калькулятор", "калькулятор"],
    "PAUSE_TIMER_COMMANDS": ["останови таймер", "пауза таймер", "поставь таймер на паузу", "приостанови таймер",
                             "стоп таймер"],
    "RESUME_TIMER_COMMANDS": ["продолжи таймер", "возобнови таймер", "запусти таймер дальше", "возобновить таймер"]
}

# Команды на английском языке
EN_COMMANDS = {
    "TIMER_COMMANDS": ["set timer", "start timer", "timer for"],
    "CLOSE_ALL_TIMERS_COMMANDS": ["close all timers", "turn off all timers", "stop all timers", "delate all timers",
                                  "stop all timer", "delete all timer"],
    "TIME_COMMANDS": ["tell time", "what time", "what's the time", "current time"],
    "WEATHER_COMMANDS": ["weather", "how's the weather", "is it warm", "temperature", "how many degrees"],
    "RADIO_ON_COMMANDS": ["turn on radio", "play radio", "open radio"],
    "RADIO_OFF_COMMANDS": ["turn off radio", "stop radio", "close radio"],
    "GREETING_COMMANDS": ["hello", "hi"],
    "THANKS_COMMANDS": ["thank you", "thanks"],
    "SHUTDOWN_COMMANDS": ["shutdown computer", "turn off computer"],
    "MUSIC_ON_COMMANDS": ["play music", "turn on music"],
    "MUSIC_OFF_COMMANDS": ["stop music", "turn off music"],
    "CALCULATOR_COMMANDS": ["open calculator", "start calculator", "launch calculator", "calculator"],
    "PAUSE_TIMER_COMMANDS": ["pause timer", "stop timer", "hold timer"],
    "RESUME_TIMER_COMMANDS": ["resume timer", "continue timer", "start timer again"]
}

# Словари сообщений
MESSAGES = {
    "ru": {
        "assistant_active": "Ассистент активен",
        "no_internet": "Интернет отсутствует, жду подключения...",
        "microphone_disconnected": "Микрофон был отключен. Ожидание...",
        "program_terminated": "Программа завершена пользователем",
        "critical_error": "Критическая ошибка: {}",
        "not_understood": "Я вас не понял. Попробуйте снова.",
        "error_occurred": "Произошла ошибка: {}",
        "unknown_error": "Произошла неизвестная ошибка. Попробуйте снова."
    },
    "en": {
        "assistant_active": "Assistant is active",
        "no_internet": "No internet connection, waiting...",
        "microphone_disconnected": "Microphone disconnected. Waiting...",
        "program_terminated": "Program terminated by user",
        "critical_error": "Critical error: {}",
        "not_understood": "I didn't understand. Please try again.",
        "error_occurred": "An error occurred: {}",
        "unknown_error": "An unknown error occurred. Please try again."
    }
}


def set_language(lang):
    """
    Устанавливает текущий язык ассистента.
    
    Args:
        lang (str): Код языка ("ru" или "en")
    
    Returns:
        str: Установленный код языка
    """
    import config
    if lang in ["ru", "en"]:
        config.LANGUAGE = lang
    return config.LANGUAGE


def get_current_language():
    """
    Возвращает текущий язык ассистента.
    
    Returns:
        str: Текущий код языка
    """
    from config import LANGUAGE
    return LANGUAGE


def get_commands(command_type):
    """
    Возвращает команды указанного типа для текущего языка.
    
    Args:
        command_type (str): Тип команды (например, "TIMER_COMMANDS")
    
    Returns:
        list: Список команд указанного типа
    """
    from config import LANGUAGE
    commands = EN_COMMANDS if LANGUAGE == "en" else RU_COMMANDS
    return commands.get(command_type, [])


def get_message(key, *args):
    """
    Возвращает сообщение по ключу для текущего языка.
    
    Args:
        key (str): Ключ сообщения
        *args: Аргументы для форматирования строки
    
    Returns:
        str: Сообщение на выбранном языке
    """
    from config import LANGUAGE
    messages = MESSAGES.get(LANGUAGE, MESSAGES["en"])
    message = messages.get(key, key)

    if args:
        try:
            return message.format(*args)
        except:
            return message
    return message
