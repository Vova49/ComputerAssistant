import os
import re
import subprocess
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta

import keyboard
import pyautogui
import pygame
import pygetwindow as gw
import pyttsx3
import requests
import speech_recognition as sr
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from speech_recognition.exceptions import RequestError

kmplayer_process = None

# Инициализация голосового движка
engine = pyttsx3.init()
timer_threads = []
timer_windows = []  # Список для хранения окон таймеров

number_words = {
    "первый": 1, "второй": 2, "третий": 3, "четвертый": 4, "пятый": 5,
    "шестой": 6, "седьмой": 7, "восьмой": 8, "девятый": 9, "десятый": 10,
    "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
    "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10
}

# Регистрация браузера Chrome
webbrowser.register("chrome", None,
                    webbrowser.BackgroundBrowser(r"C:\Program Files\Google\Chrome\Application\chrome.exe"))


def create_circular_timer(seconds):
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=seconds)
    end_time_str = end_time.strftime("%H:%M")

    def update_timer():
        nonlocal seconds, force_stop
        if seconds >= 0 and not stop_event.is_set():
            canvas.delete("all")
            draw_timer(seconds)
            seconds -= 1
            root.after(1000, update_timer)
        else:
            if not force_stop:
                set_volume(22)
                play_sound()
            root.after(3000, root.quit)

    def draw_timer(time_left):
        canvas.create_oval(30, 30, 270, 270, outline="black", width=9)
        hours, remainder = divmod(time_left, 3600)
        minutes, secs = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{secs:02}" if hours > 0 else f"{minutes:02}:{secs:02}"
        canvas.create_text(150, 130, text=time_str, font=("Arial", 40, "bold"), fill="red")

        angle = -((time_left / total_seconds) * 360)
        canvas.create_arc(30, 30, 270, 270, start=90, extent=angle, outline="red", width=10, style=tk.ARC)

        canvas.create_text(150, 180, text=f"Закончится в {end_time_str}", font=("Arial", 14), fill="black")

    def start_move(event):
        root.x = event.x
        root.y = event.y

    def move_window(event):
        x = root.winfo_x() + (event.x - root.x)
        y = root.winfo_y() + (event.y - root.y)
        root.geometry(f"+{x}+{y}")

    root = tk.Tk()
    root.geometry("300x315")  # Увеличил высоту для заголовка
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.overrideredirect(True)  # Убираем заголовок окна

    timer_number = len(timer_windows) + 1
    label = tk.Label(root, text=f"Таймер {timer_number}", font=("Arial", 12, "bold"), bg="white")
    label.pack()

    canvas = tk.Canvas(root, width=300, height=300, bg="white")
    canvas.pack()

    canvas.bind("<ButtonPress-1>", start_move)
    canvas.bind("<B1-Motion>", move_window)

    global total_seconds
    total_seconds = seconds

    stop_event = threading.Event()
    force_stop = False

    timer_windows.append((timer_number, root, stop_event, lambda: set_force_stop()))

    def set_force_stop():
        nonlocal force_stop
        force_stop = True

    update_timer()
    root.mainloop()
    stop_event.set()


def start_timer_thread(seconds):
    """Запуск таймера в отдельном потоке."""
    timer_thread = threading.Thread(target=create_circular_timer, args=(seconds,))
    timer_threads.append(timer_thread)
    timer_thread.start()


def close_timer_by_number(n):
    """Закрывает таймер с указанным номером."""
    global timer_windows
    for timer in timer_windows:
        if timer[0] == n:
            _, window, stop_event, set_force_stop = timer
            set_force_stop()
            stop_event.set()
            window.quit()
            timer_windows.remove(timer)
            print(f"Таймер {n} закрыт")
            return
    print(f"Таймер {n} не найден")


def close_all_timers():
    """Закрывает все таймеры без звука."""
    global timer_windows
    for window, stop_event, set_force_stop in timer_windows:
        set_force_stop()  # Устанавливаем флаг принудительной остановки
        stop_event.set()  # Останавливаем таймер
        window.quit()  # Закрываем окно
    timer_windows.clear()


def play_sound():
    """Воспроизводит звуковой файл с использованием pygame."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(r"C:/Users/vovaf/PycharmProjects/ComputerAssistant/signal.mp3")  # Путь к файлу
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Ошибка при воспроизведении звука: {e}")


def speak(text):
    """Произносит текст вслух."""
    engine.say(text)
    engine.runAndWait()


def parse_time(command):
    try:
        # Ищем все значения времени в формате: число и единица измерения (если есть)
        time_parts = re.findall(r"(\d+)\s*(час[а-я]*|минут[а-я]*|секунд[а-я]*)?", command)
        total_seconds = 0

        for value, unit in time_parts:
            value = int(value)
            if not unit or unit.strip() == "":  # Если единица измерения не указана, считаем минуты
                total_seconds += value * 60
            elif "час" in unit:
                total_seconds += value * 3600  # Переводим часы в секунды
            elif "минут" in unit or "минута" in unit:
                total_seconds += value * 60  # Переводим минуты в секунды
            elif "секунд" in unit or "секунда" in unit:
                total_seconds += value  # Секунды не нужно переводить

        return total_seconds if total_seconds > 0 else None
    except ValueError:
        return None


def ensure_sound_on():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume = interface.QueryInterface(IAudioEndpointVolume)

        # Проверяем состояние громкости
        mute = volume.GetMute()
        if mute:
            volume.SetMute(0, None)  # Снимаем отключение звука
            print("Звук был отключен. Включаю.")
        else:
            print("Звук уже включен.")

    except Exception as e:
        print(f"Не удалось проверить или включить звук: {e}")


def set_volume(level):
    if 0 <= level <= 100:
        try:
            ensure_sound_on()  # Убедиться, что звук включен
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = interface.QueryInterface(IAudioEndpointVolume)
            # Устанавливаем громкость (уровень в диапазоне от 0.0 до 1.0)
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            print(f"Громкость установлена на {level}%.")
        except Exception as e:
            print(f"Не удалось установить громкость: {e}")
    else:
        print("Уровень громкости должен быть от 0 до 100.")


def search_movie_on_kinogo(movie_name):
    base_url = "https://kinogo.ec/index.php?do=search"
    query = f"&subaction=search&story={movie_name.replace(' ', '+')}"
    search_url = base_url + query
    try:
        webbrowser.get("chrome").open_new_tab(search_url)
        print(f"Ищу фильм {movie_name} на Kinogo.")
        print(f"Открываю {search_url}")
    except webbrowser.Error:
        print("Не удалось открыть браузер. Проверьте, установлен ли Chrome.")


def open_video(url):
    """Открывает видео в браузере."""
    try:
        webbrowser.get("chrome").open_new_tab(url)  # Открываем URL в Chrome
        print("Включаю видео.")
    except webbrowser.Error:
        print("Не удалось открыть браузер. Проверьте, установлен ли Chrome.")


def get_current_weather(city="Sveti Vlas"):
    """Получает текущую погоду в городе."""
    api_key = "f9e802139fd047962b02a8ff0af7c606"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            return f"Сейчас в {city}: {temp} градусов, {weather}"
        else:
            return f"Ошибка: {data.get('message', 'Не удалось получить данные')}"
    except Exception as e:
        return f"Ошибка запроса: {e}"


def play_music(folder_path):
    """Открывает папку с музыкой в KMPlayer."""
    global kmplayer_process
    kmplayer_path = r"C:\Program Files (x86)\KMPlayer\KMPlayer.exe"  # Укажите путь к KMPlayer
    if os.path.exists(folder_path) and os.path.exists(kmplayer_path):
        try:
            # Запускаем плеер и сохраняем процесс
            set_volume(24)
            kmplayer_process = subprocess.Popen([kmplayer_path, folder_path])
            print("Включаю музыку.")
        except Exception as e:
            print(f"Произошла ошибка при запуске плеера: {e}")
    else:
        speak("Не могу найти плеер или папку с музыкой.")


def stop_music():
    """Останавливает KMPlayer."""
    global kmplayer_process
    if kmplayer_process:
        try:
            # Завершаем процесс KMPlayer
            kmplayer_process.terminate()  # Посылает сигнал завершения
            kmplayer_process = None
            print("Музыка выключена.")
        except Exception as e:
            speak(f"Не удалось выключить музыку: {e}")
    else:
        speak("Музыка сейчас не играет.")


def turn_on_radio():
    windows = gw.getWindowsWithTitle("Google Chrome")
    if windows:
        win = windows[0]  # Берем первое найденное окно
        win.activate()  # Активируем его

    keyboard.press_and_release('ctrl+1')
    time.sleep(0.3)
    pyautogui.click(1125, 210)


def check_internet():
    """ Проверяет наличие интернета, делая запрос к Google. """
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False


def process_timer_command(command):
    """Обрабатывает команды, связанные с таймерами."""
    if any(word in command for word in ["включи таймер", "поставь таймер", "засеки", "запусти таймер"]):
        minutes = parse_time(command)
        if minutes:
            start_timer_thread(minutes)
            speak(f"Таймер поставлен.")
        else:
            speak("Не удалось определить время таймера")

    elif "закрой все таймеры" in command or "выключи все таймеры" in command:
        close_all_timers()
        speak("Все таймеры выключены.")

    else:
        match = re.search(r"(закрой|выключи) (\d+|[а-я]+)[^\d]*таймер", command)
        if match:
            number_str = match.group(2)
            timer_number = int(number_str) if number_str.isdigit() else number_words.get(number_str, None)
            if timer_number:
                close_timer_by_number(timer_number)
            else:
                speak("Не удалось определить номер таймера.")


def process_video_command(command):
    """Обрабатывает команды по включению видео."""
    movie_name = command.replace("включи", "").strip()
    if "фиксиков" in movie_name or "фиксики" in movie_name:
        open_video("https://www.youtube.com/watch?v=FG26F4FwGuE&ab_channel=%D0%A4%D0%B8%D0%BA%D0%B8%D0%B8")
    elif "смешариков" in movie_name or "смешарики" in movie_name:
        open_video("https://www.youtube.com/watch?v=FfDRfz9Bl0k&ab_channel=TVSmeshariki")
    else:
        search_movie_on_kinogo(movie_name)


def main():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ассистент активен")
        while True:
            try:
                # Проверяем подключение к интернету перед началом работы
                while not check_internet():
                    print("Интернет отсутствует, жду подключения...")
                    time.sleep(5)

                print("Говорите...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio, language="ru-RU").lower()
                print(f"Вы сказали: {command}")

                # Обработка команд
                if "привет" in command:
                    speak("Привет!")
                elif any(word in command for word in ["скажи время", "какое время", "который час"]):
                    speak(f"Сейчас {datetime.now().strftime('%H:%M')}")
                elif "спасибо" in command or "благодарю" in command:
                    speak("Пожалуйста")
                elif "выключи компьютер" in command:
                    os.system("shutdown /s /t 0")

                # Управление таймерами
                elif "таймер" in command:
                    process_timer_command(command)

                # Управление музыкой
                elif "выключи музыку" in command:
                    stop_music()
                elif "включи музыку" in command:
                    set_volume(20)
                    play_music(r"D:\\музыка\\Настроение")  # Укажите путь к вашей папке с музыкой

                # Управление радио
                elif "включи радио" in command or "выключи радио" in command:
                    set_volume(20)
                    turn_on_radio()

                # Погода
                elif any(word in command for word in ["погода", "какая погода", "сейчас тепло", "сколько градусов"]):
                    set_volume(20)
                    speak(get_current_weather())

                # Воспроизведение видео
                elif "включи" in command:
                    process_video_command(command)

                else:
                    print("Я вас не понял. Попробуйте снова.")

            except sr.UnknownValueError:
                print("Не могу распознать, попробуйте снова.")
            except sr.WaitTimeoutError:
                print("Микрофон не обнаружил звук, жду дальше.")
            except RequestError:
                print("Ошибка сети. Проверьте интернет и попробуйте снова.")
            except Exception as e:
                print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    set_volume(20)
    speak(get_current_weather())
    main()
