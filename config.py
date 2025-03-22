"""
Конфигурационный файл для голосового ассистента.
Содержит все настройки и пути, используемые в приложении.
"""

# Пути к файлам и директориям
MUSIC_FOLDER = r"D:\музыка\Настроение"
SOUND_SIGNAL_PATH = r"C:/Users/vovaf/PycharmProjects/ComputerAssistant/signal.mp3"
KMPLAYER_PATH = r"C:\Program Files (x86)\KMPlayer\KMPlayer.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Настройки громкости
DEFAULT_VOLUME = 20
TIMER_VOLUME = 22
WEATHER_VOLUME = 20
RADIO_VOLUME = 20

# Настройки погоды
WEATHER_API_KEY = "f9e802139fd047962b02a8ff0af7c606"
DEFAULT_CITY = "Sveti Vlas"

# Настройки таймера
TIMER_WINDOW_WIDTH = 300
TIMER_WINDOW_HEIGHT = 315

# Настройки радио
# Описания действий для открытия радио
RADIO_BROWSER_TAB = 1  # Номер вкладки в Chrome

# Команды
TIMER_COMMANDS = ["включи таймер", "поставь таймер", "засеки", "запусти таймер", "таймер на"]
CLOSE_ALL_TIMERS_COMMANDS = ["закрой все таймеры", "выключи все таймеры", "закрой все таймер", "выключи все таймер"]
TIME_COMMANDS = ["скажи время", "какое время", "который час"]
WEATHER_COMMANDS = ["погода", "какая погода", "сейчас тепло", "сколько градусов"]
RADIO_ON_COMMANDS = ["включи радио"]
RADIO_OFF_COMMANDS = ["выключи радио"]
