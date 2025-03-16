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
    root.geometry("300x300")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.overrideredirect(True)  # Убираем заголовок окна

    canvas = tk.Canvas(root, width=300, height=300, bg="white")
    canvas.pack()

    canvas.bind("<ButtonPress-1>", start_move)
    canvas.bind("<B1-Motion>", move_window)

    global total_seconds
    total_seconds = seconds

    stop_event = threading.Event()
    force_stop = False

    timer_windows.append((root, stop_event, lambda: set_force_stop()))

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


def main():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ассистент активен")
        while True:
            try:
                # Проверяем интернет перед распознаванием
                while not check_internet():
                    print("Интернет отсутствует, жду подключения...")
                    time.sleep(5)  # Ждём 5 секунд перед новой проверкой

                print("Говорите...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio, language="ru-RU").lower()
                print(f"Вы сказали: {command}")

                # Реакция на команды
                if "привет" in command:
                    speak("Привет!")
                elif "скажи время" in command or " какое время" in command:
                    current_time = datetime.now().strftime("%H:%M")
                    speak(f"Сейчас {current_time}")
                if "Спасибо" in command or "Благодарю" in command:
                    speak("Пожалуйста")
                elif "выключи компьютер" in command:
                    os.system("shutdown /s /t 0")
                elif "выключи таймер" in command or "выключи таймеры" in command or "закрой таймер" in command:
                    close_all_timers()
                elif "выключи музыку" in command:
                    stop_music()
                elif "включи музыку" in command or "включи музыка" in command:
                    set_volume(20)
                    music_folder = r"D:\музыка\Настроение"  # Укажите путь к вашей папке с музыкой
                    play_music(music_folder)
                elif "включи радио" in command or "выключи радио" in command or "закрой радио" in command:
                    set_volume(20)
                    turn_on_radio()
                elif "погода" in command or "Какая погода" in command or "Сейчас тепло" in command or "Сегодня будет тепло" in command or "Сколько градусов" in command:
                    set_volume(20)
                    speak(get_current_weather())
                elif "включи" in command:
                    if "таймер" in command:  # Если в команде упоминается "таймер", обрабатываем это отдельно
                        minutes = parse_time(command)
                        if minutes:
                            start_timer_thread(minutes)  # Запускаем таймер на нужное количество секунд
                            set_volume(20)
                            speak(f"Таймер поставлен")
                        else:
                            speak("Повторите пожалуйста")
                    else:
                        # Убираем "включи" из команды и очищаем от лишних пробелов для запуска видео
                        movie_name = command.replace("включи", "").strip()
                        # Проверяем специальные случаи
                        if "фиксиков" in movie_name or "фиксики" in movie_name:
                            video_url = "https://www.youtube.com/watch?v=FG26F4FwGuE&ab_channel=%D0%A4%D0%B8%D0%BA%D0%B8%D0%B8"
                            open_video(video_url)
                        elif "смешариков" in movie_name or "смешарики" in movie_name:
                            video_url = "https://www.youtube.com/watch?v=FfDRfz9Bl0k&ab_channel=TVSmeshariki"
                            open_video(video_url)
                        else:
                            # Если команда не содержит фиксиков или смешариков, ищем на kinogo.ec
                            search_movie_on_kinogo(movie_name)

                elif "включи таймер" in command or "поставь таймер" in command or "засеки" in command or "запусти таймер" in command or "таймер" in command:
                    # Пытаемся извлечь количество минут из команды
                    minutes = parse_time(command)
                    if minutes:
                        start_timer_thread(minutes)
                        set_volume(20)
                        speak(f"Таймер поставлен")
                    else:
                        speak("Повторите пожалуйста")
                else:
                    print("Я вас не понял. Попробуйте снова.")
            except sr.UnknownValueError:
                print("Не могу распознать, попробуйте снова.")
            except sr.WaitTimeoutError:
                print("Микрофон не обнаружил звук, жду дальше.")
            except RequestError as e:
                print("Убедитесь, что подключение к интернету активно, и попробуйте снова.")
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    set_volume(20)
    speak(get_current_weather())
    main()
