import os
import webbrowser

from audio_manager import speak
from config import CHROME_PATH, LANGUAGE

# Проверка наличия браузера Chrome
chrome_exists = os.path.exists(CHROME_PATH)

# Регистрация браузера Chrome, если он найден
if chrome_exists:
    try:
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(CHROME_PATH))
        if LANGUAGE == "en":
            print("Chrome successfully registered")
        else:
            print("Chrome успешно зарегистрирован")
    except webbrowser.Error as e:
        if LANGUAGE == "en":
            print(f"Error registering Chrome: {e}")
        else:
            print(f"Ошибка регистрации Chrome: {e}")


def search_movie_on_kinogo(movie_name):
    """
    Выполняет поиск фильма на сайте Kinogo.
    
    Args:
        movie_name (str): Название фильма для поиска
    """
    base_url = "https://kinogo.ec/index.php?do=search"
    query = f"&subaction=search&story={movie_name.replace(' ', '+')}"
    search_url = base_url + query
    try:
        if not chrome_exists:
            if LANGUAGE == "en":
                print("Chrome not found, using default browser")
            else:
                print("Chrome не найден, используем браузер по умолчанию")
            webbrowser.open_new_tab(search_url)
        else:
            webbrowser.get("chrome").open_new_tab(search_url)

        if LANGUAGE == "en":
            print(f"Searching for movie {movie_name} on Kinogo.")
            print(f"Opening {search_url}")
        else:
            print(f"Ищу фильм {movie_name} на Kinogo.")
            print(f"Открываю {search_url}")
    except webbrowser.Error as e:
        if LANGUAGE == "en":
            print(f"Failed to open browser: {e}")
            speak("Failed to open browser to search for the movie")
        else:
            print(f"Не удалось открыть браузер: {e}")
            speak("Не удалось открыть браузер для поиска фильма")


def open_video(url):
    """
    Открывает видео в браузере.
    
    Args:
        url (str): URL видео для открытия
    """
    try:
        if not chrome_exists:
            if LANGUAGE == "en":
                print("Chrome not found, using default browser")
            else:
                print("Chrome не найден, используем браузер по умолчанию")
            webbrowser.open_new_tab(url)
        else:
            webbrowser.get("chrome").open_new_tab(url)

        if LANGUAGE == "en":
            print(f"Playing video: {url}")
        else:
            print(f"Включаю видео: {url}")
    except webbrowser.Error as e:
        if LANGUAGE == "en":
            print(f"Failed to open browser: {e}")
            speak("Failed to open browser to play video")
        else:
            print(f"Не удалось открыть браузер: {e}")
            speak("Не удалось открыть браузер для воспроизведения видео")


def process_video_command(command):
    """
    Обрабатывает команды по включению видео.
    
    Args:
        command (str): Команда для обработки
    """
    try:
        if LANGUAGE == "en":
            movie_name = command.replace("play", "").strip()
        else:
            movie_name = command.replace("включи", "").strip()

        if not movie_name:
            if LANGUAGE == "en":
                speak("Please specify a video or movie name")
            else:
                speak("Пожалуйста, укажите название видео или фильма")
            return

        # Проверяем ключевые слова для мультфильмов
        if LANGUAGE == "en":
            if "fixiki" in movie_name or "fixies" in movie_name:
                open_video("https://www.youtube.com/watch?v=FG26F4FwGuE&ab_channel=%D0%A4%D0%B8%D0%BA%D0%B8%D0%B8")
            elif "smeshariki" in movie_name or "kikoriki" in movie_name:
                open_video("https://www.youtube.com/watch?v=FfDRfz9Bl0k&ab_channel=TVSmeshariki")
            else:
                search_movie_on_kinogo(movie_name)
        else:
            if "фиксиков" in movie_name or "фиксики" in movie_name:
                open_video("https://www.youtube.com/watch?v=FG26F4FwGuE&ab_channel=%D0%A4%D0%B8%D0%BA%D0%B8%D0%B8")
            elif "смешариков" in movie_name or "смешарики" in movie_name:
                open_video("https://www.youtube.com/watch?v=FfDRfz9Bl0k&ab_channel=TVSmeshariki")
            else:
                search_movie_on_kinogo(movie_name)
    except Exception as e:
        if LANGUAGE == "en":
            print(f"Error processing video command: {e}")
            speak("An error occurred while processing the command")
        else:
            print(f"Ошибка при обработке видео-команды: {e}")
            speak("Произошла ошибка при обработке команды")
