"""
Конфигурационный файл для голосового ассистента.
Содержит все настройки и пути, используемые в приложении.
"""

import os

from language_manager import (
    get_commands
)
from utils import get_application_path

# Текущий язык ассистента
LANGUAGE = "ru"  # Доступные языки: "ru" (русский), "en" (английский)

# Пути к файлам и директориям
MUSIC_FOLDER = r"D:\музыка\Настроение"
# Определяем путь к звуковому файлу относительно папки приложения
SOUND_SIGNAL_PATH = os.path.join(get_application_path(), "signal.mp3")
KMPLAYER_PATH = r"C:\Program Files (x86)\KMPlayer\KMPlayer.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Настройки громкости
DEFAULT_VOLUME = 20
TIMER_VOLUME = 22
WEATHER_VOLUME = 20
RADIO_VOLUME = 20

# Настройки речи и звука
SPEECH_RATE = 200  # Скорость речи (стандартное значение 200, увеличение ускоряет речь)
VOICE_VOLUME = 1.0  # Громкость речи (от 0 до 1)
PYGAME_BUFFER = 512  # Буфер для воспроизведения звука (меньшее значение - быстрее, но может быть нестабильно)
SPEECH_ENERGY_THRESHOLD = 280  # Порог энергии для распознавания речи (300 стандарт, меньше - чувствительнее)
SPEECH_PAUSE_THRESHOLD = 0.5  # Секунд паузы для определения окончания фразы (меньше - быстрее реакция)
SPEECH_RECOGNITION_TIMEOUT = 2  # Время ожидания фразы в секундах

# Настройки погоды
WEATHER_API_KEY = "f9e802139fd047962b02a8ff0af7c606"
DEFAULT_CITY = "Sveti Vlas"

# Настройки таймера
TIMER_WINDOW_WIDTH = 300
TIMER_WINDOW_HEIGHT = 315

# Настройки радио
# Описания действий для открытия радио
RADIO_BROWSER_TAB = 1  # Номер вкладки в Chrome

# Получаем актуальные команды в зависимости от выбранного языка
TIMER_COMMANDS = get_commands("TIMER_COMMANDS")
CLOSE_ALL_TIMERS_COMMANDS = get_commands("CLOSE_ALL_TIMERS_COMMANDS")
TIME_COMMANDS = get_commands("TIME_COMMANDS")
WEATHER_COMMANDS = get_commands("WEATHER_COMMANDS")
RADIO_ON_COMMANDS = get_commands("RADIO_ON_COMMANDS")
RADIO_OFF_COMMANDS = get_commands("RADIO_OFF_COMMANDS")
CALCULATOR_COMMANDS = get_commands("CALCULATOR_COMMANDS")
PAUSE_TIMER_COMMANDS = get_commands("PAUSE_TIMER_COMMANDS")
RESUME_TIMER_COMMANDS = get_commands("RESUME_TIMER_COMMANDS")
