import queue
import re
import threading
import tkinter as tk
from datetime import datetime, timedelta

from audio_manager import set_volume, play_sound, speak
from config import TIMER_VOLUME, TIMER_WINDOW_WIDTH, TIMER_WINDOW_HEIGHT, LANGUAGE

timer_threads = []
timer_windows = []
next_timer_number = 1
timer_queue = queue.Queue()
# Добавляем мьютекс для синхронизации доступа к общим ресурсам
timer_lock = threading.Lock()

# Словари для числительных на разных языках
number_words = {
    "ru": {
        "первый": 1, "второй": 2, "третий": 3, "четвертый": 4, "пятый": 5,
        "шестой": 6, "седьмой": 7, "восьмой": 8, "девятый": 9, "десятый": 10,
        "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
        "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10
    },
    "en": {
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
}


def process_timer_command(command):
    """Обрабатывает команды, связанные с таймерами."""
    from config import TIMER_COMMANDS, CLOSE_ALL_TIMERS_COMMANDS

    try:
        if LANGUAGE == "en":
            # Проверка команды "timer for X minutes" на английском
            timer_for_pattern = re.search(r"timer for (\d+) (minutes|minute)", command)
            if timer_for_pattern:
                minutes = int(timer_for_pattern.group(1))
                if minutes > 0:
                    start_timer_thread(minutes * 60)  # Переводим минуты в секунды
                    speak(f"Timer set for {minutes} minutes.")
                    return
                else:
                    speak("Please specify a time greater than zero.")
                    return
        else:
            # Проверка команды "таймер на X минут" на русском
            timer_на_pattern = re.search(r"таймер на (\d+) (минут|минуты|минуту)", command)
            if timer_на_pattern:
                minutes = int(timer_на_pattern.group(1))
                if minutes > 0:
                    start_timer_thread(minutes * 60)  # Переводим минуты в секунды
                    speak(f"Таймер на {minutes} минут поставлен.")
                    return
                else:
                    speak("Укажите время больше нуля.")
                    return

        if any(word in command for word in TIMER_COMMANDS):
            from utils import parse_time
            minutes = parse_time(command)
            if minutes:
                start_timer_thread(minutes)
                if LANGUAGE == "en":
                    speak("Timer set.")
                else:
                    speak("Таймер поставлен.")
            else:
                if LANGUAGE == "en":
                    speak("Could not determine timer duration")
                else:
                    speak("Не удалось определить время таймера")

        elif any(word in command for word in CLOSE_ALL_TIMERS_COMMANDS):
            close_all_timers()
            if LANGUAGE == "en":
                speak("All timers turned off.")
            else:
                speak("Все таймеры выключены.")

        else:
            # Регулярное выражение для обработки команды закрытия таймера
            if LANGUAGE == "en":
                match = re.search(r"(close|turn off) (\d+|[a-z]+)[^\d]*timer", command)
                words_dict = number_words["en"]
            else:
                match = re.search(r"(закрой|выключи) (\d+|[а-я]+)[^\d]*таймер", command)
                words_dict = number_words["ru"]
                
            if match:
                number_str = match.group(2)
                timer_number = int(number_str) if number_str.isdigit() else words_dict.get(number_str, None)
                if timer_number:
                    if close_timer_by_number(timer_number):
                        if LANGUAGE == "en":
                            speak(f"Timer {timer_number} closed")
                        else:
                            speak(f"Таймер {timer_number} закрыт")
                    else:
                        if LANGUAGE == "en":
                            speak(f"Could not close timer {timer_number}")
                        else:
                            speak(f"Не удалось закрыть таймер {timer_number}")
                else:
                    if LANGUAGE == "en":
                        speak("Could not determine timer number.")
                    else:
                        speak("Не удалось определить номер таймера.")
    except Exception as e:
        if LANGUAGE == "en":
            print(f"Error processing timer command: {e}")
            speak("An error occurred while working with the timer")
        else:
            print(f"Ошибка при обработке команды таймера: {e}")
            speak("Произошла ошибка при работе с таймером")


def update_timer_ui():
    """Обновляет интерфейс таймеров."""
    try:
        while True:
            try:
                window, new_number = timer_queue.get_nowait()
                for widget in window.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(text=f"Таймер {new_number}")
                        break
            except queue.Empty:
                break
            except Exception as e:
                print(f"Ошибка при обновлении UI таймера: {e}")
                break
    except Exception as e:
        print(f"Ошибка при обработке очереди таймеров: {e}")


def cleanup_dead_threads():
    """Очищает список от завершенных потоков."""
    global timer_threads
    try:
        with timer_lock:  # Синхронизация доступа к timer_threads
            timer_threads = [thread for thread in timer_threads if thread.is_alive()]
            print(f"Очистка потоков. Осталось активных потоков: {len(timer_threads)}")
    except Exception as e:
        print(f"Ошибка при очистке потоков: {e}")


def update_timer_numbers():
    global next_timer_number
    try:
        with timer_lock:  # Синхронизация доступа к timer_windows и next_timer_number
            print(f"Начало обновления номеров таймеров. Текущие таймеры: {timer_windows}")

            # Фильтруем недействительные таймеры
            valid_timers = []
            for timer in timer_windows:
                try:
                    _, window, _, _, _ = timer  # Обновлено для учета toggle_pause
                    if window.winfo_exists():
                        valid_timers.append(timer)
                    else:
                        print(f"Найден недействительный таймер: {timer}")
                except Exception as e:
                    print(f"Ошибка при проверке таймера: {e}")
                    continue

            timer_windows.clear()
            timer_windows.extend(valid_timers)

            # Сортируем таймеры по текущим номерам
            timer_windows.sort(key=lambda x: x[0])

            new_timer_windows = []
            for i, timer in enumerate(timer_windows, 1):
                old_number, window, stop_event, set_force_stop, toggle_pause = timer  # Обновлено для учета toggle_pause
                if old_number != i:
                    print(f"Обновление номера таймера с {old_number} на {i}")
                    try:
                        timer_queue.put((window, i))
                    except Exception as e:
                        print(f"Ошибка при обновлении номера таймера: {e}")
                new_timer_windows.append(
                    (i, window, stop_event, set_force_stop, toggle_pause))  # Обновлено для учета toggle_pause

            timer_windows.clear()
            timer_windows.extend(new_timer_windows)

            next_timer_number = len(timer_windows) + 1
    except Exception as e:
        print(f"Ошибка при обновлении номеров таймеров: {e}")


def create_circular_timer(seconds):
    global next_timer_number
    try:
        if LANGUAGE == "en":
            print(f"Creating new timer for {seconds} seconds")
        else:
            print(f"Создание нового таймера на {seconds} секунд")
            
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=seconds)
        end_time_str = end_time.strftime("%H:%M")

        def update_timer():
            nonlocal seconds, force_stop
            # Убираем обращение к глобальной переменной total_seconds
            nonlocal total_seconds, is_paused
            try:
                if seconds >= 0 and not stop_event.is_set():
                    canvas.delete("all")
                    draw_timer(seconds)
                    if not is_paused:
                        seconds -= 1
                    root.after(1000, update_timer)
                else:
                    if not force_stop:
                        set_volume(TIMER_VOLUME)
                        play_sound()
                    root.after(3000, root.quit)
            except Exception as e:
                if LANGUAGE == "en":
                    print(f"Error in update_timer: {e}")
                else:
                    print(f"Ошибка в update_timer: {e}")
                root.quit()

        def draw_timer(time_left):
            try:
                # Используем локальную переменную total_seconds
                nonlocal total_seconds, is_paused
                canvas.create_oval(30, 30, 270, 270, outline="black", width=9)
                hours, remainder = divmod(time_left, 3600)
                minutes, secs = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{secs:02}" if hours > 0 else f"{minutes:02}:{secs:02}"

                # Уменьшаем размер шрифта, если отображаются часы
                font_size = 40 if hours == 0 else 30

                canvas.create_text(150, 130, text=time_str, font=("Arial", font_size, "bold"), fill="red")

                angle = -((time_left / total_seconds) * 360)
                canvas.create_arc(30, 30, 270, 270, start=90, extent=angle, outline="red", width=10, style=tk.ARC)

                if LANGUAGE == "en":
                    canvas.create_text(150, 180, text=f"Ends at {end_time_str}", font=("Arial", 14), fill="black")
                    pause_button_text = "Pause" if not is_paused else "Resume"
                else:
                    canvas.create_text(150, 180, text=f"Закончится в {end_time_str}", font=("Arial", 14), fill="black")
                    pause_button_text = "Пауза" if not is_paused else "Продолжить"

                # Изменяем текст на кнопке в зависимости от состояния таймера
                pause_button.config(text=pause_button_text)

                # Позиционируем кнопку на канвасе
                canvas.create_window(150, 210, window=pause_button)
                
            except Exception as e:
                if LANGUAGE == "en":
                    print(f"Error in draw_timer: {e}")
                else:
                    print(f"Ошибка в draw_timer: {e}")

        def toggle_pause():
            nonlocal is_paused
            is_paused = not is_paused
            if LANGUAGE == "en":
                print(f"Timer {'paused' if is_paused else 'resumed'}")
            else:
                print(f"Таймер {'приостановлен' if is_paused else 'возобновлен'}")
            draw_timer(seconds)

        def start_move(event):
            root.x = event.x
            root.y = event.y

        def move_window(event):
            x = root.winfo_x() + (event.x - root.x)
            y = root.winfo_y() + (event.y - root.y)
            root.geometry(f"+{x}+{y}")

        def on_closing():
            nonlocal force_stop
            try:
                force_stop = True
                stop_event.set()
                root.quit()
            except Exception as e:
                if LANGUAGE == "en":
                    print(f"Error when closing timer: {e}")
                else:
                    print(f"Ошибка при закрытии таймера: {e}")

        def cleanup_timer_on_exit():
            """Удаляет запись таймера из списка после завершения"""
            nonlocal timer_number
            try:
                with timer_lock:
                    for i, timer in enumerate(timer_windows):
                        if timer[0] == timer_number:
                            timer_windows.pop(i)
                            break
                update_timer_numbers()
                cleanup_dead_threads()
                print(f"Таймер {timer_number} удален после завершения")
            except Exception as e:
                print(f"Ошибка при очистке таймера: {e}")

        root = tk.Tk()
        root.geometry(f"{TIMER_WINDOW_WIDTH}x{TIMER_WINDOW_HEIGHT}")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        root.overrideredirect(True)
        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Получаем номер таймера с синхронизацией
        with timer_lock:
            timer_number = next_timer_number
            next_timer_number += 1

        if LANGUAGE == "en":
            label = tk.Label(root, text=f"Timer {timer_number}", font=("Arial", 12, "bold"), bg="white")
        else:
            label = tk.Label(root, text=f"Таймер {timer_number}", font=("Arial", 12, "bold"), bg="white")
        label.pack(pady=(5, 0))

        canvas = tk.Canvas(root, width=TIMER_WINDOW_WIDTH, height=TIMER_WINDOW_HEIGHT - 25, bg="white")
        canvas.pack()

        # Создаем кнопку с минимальным размером рамки
        pause_button_text = "Пауза" if LANGUAGE == "ru" else "Pause"
        pause_button = tk.Button(root, text=pause_button_text, command=toggle_pause,
                                 font=("Arial", 10), bg="lightblue", relief=tk.FLAT,
                                 padx=5, pady=1, borderwidth=1)

        canvas.bind("<ButtonPress-1>", start_move)
        canvas.bind("<B1-Motion>", move_window)

        # Создаем локальную переменную total_seconds вместо глобальной
        total_seconds = seconds
        is_paused = False

        stop_event = threading.Event()
        force_stop = False

        # Добавление таймера в список с синхронизацией
        with timer_lock:
            timer_windows.append((timer_number, root, stop_event, lambda: set_force_stop(), toggle_pause))

        def set_force_stop():
            nonlocal force_stop
            force_stop = True

        update_timer()
        # Регистрируем функцию очистки, которая будет выполнена после завершения mainloop
        root.after(total_seconds * 1000 + 3500, cleanup_timer_on_exit)
        root.mainloop()
        stop_event.set()
    except Exception as e:
        if LANGUAGE == "en":
            print(f"Error creating timer: {e}")
        else:
            print(f"Ошибка при создании таймера: {e}")


def start_timer_thread(seconds):
    try:
        cleanup_dead_threads()
        timer_thread = threading.Thread(target=create_circular_timer, args=(seconds,))
        timer_thread.daemon = True  # Делаем поток демоном

        # Добавление в список потоков с синхронизацией
        with timer_lock:
            timer_threads.append(timer_thread)

        timer_thread.start()
    except Exception as e:
        print(f"Ошибка при запуске потока таймера: {e}")


def close_timer_by_number(n):
    global timer_windows
    try:
        with timer_lock:  # Синхронизация доступа к timer_windows
            print(f"Попытка закрыть таймер {n}. Текущие таймеры: {timer_windows}")

            timer_to_close = None
            for timer in timer_windows:
                try:
                    if timer[0] == n and timer[1].winfo_exists():
                        timer_to_close = timer
                        break
                except Exception as e:
                    print(f"Ошибка при проверке таймера: {e}")
                    continue

            if timer_to_close is None:
                print(f"Таймер {n} не найден")
                return False

            _, window, stop_event, set_force_stop, toggle_pause = timer_to_close
            set_force_stop()
            stop_event.set()

            try:
                window.quit()
                window.destroy()
            except Exception as e:
                print(f"Ошибка при закрытии окна таймера: {e}")

            timer_windows.remove(timer_to_close)
            print(f"Таймер {n} удален из списка. Оставшиеся таймеры: {timer_windows}")

        update_timer_numbers()
        cleanup_dead_threads()
        print(f"Таймер {n} успешно закрыт")
        return True
    except Exception as e:
        print(f"Ошибка при закрытии таймера: {e}")
        return False


def close_all_timers():
    global timer_windows, next_timer_number
    try:
        with timer_lock:  # Синхронизация доступа к timer_windows и next_timer_number
            print(f"Закрытие всех таймеров. Текущие таймеры: {timer_windows}")
            for timer in timer_windows[:]:
                try:
                    _, window, stop_event, set_force_stop, toggle_pause = timer
                    if window.winfo_exists():
                        set_force_stop()
                        stop_event.set()
                        window.quit()
                        window.destroy()
                except Exception as e:
                    print(f"Ошибка при закрытии таймера: {e}")
            timer_windows.clear()
            next_timer_number = 1
        cleanup_dead_threads()
        print("Все таймеры закрыты")
    except Exception as e:
        print(f"Ошибка при закрытии всех таймеров: {e}")


def pause_timer_by_number(n):
    """Ставит таймер на паузу по номеру."""
    global timer_windows
    try:
        with timer_lock:
            print(f"Попытка приостановить таймер {n}. Текущие таймеры: {timer_windows}")

            timer_to_pause = None
            for timer in timer_windows:
                try:
                    if timer[0] == n and timer[1].winfo_exists():
                        timer_to_pause = timer
                        break
                except Exception as e:
                    print(f"Ошибка при проверке таймера: {e}")
                    continue

            if timer_to_pause is None:
                print(f"Таймер {n} не найден")
                return False

            _, _, _, _, toggle_pause = timer_to_pause
            toggle_pause()  # Вызываем функцию переключения паузы
            print(f"Таймер {n} успешно приостановлен/возобновлен")
            return True
    except Exception as e:
        print(f"Ошибка при изменении состояния таймера: {e}")
        return False


def process_pause_resume_timer_command(command):
    """Обрабатывает команды паузы и возобновления таймера."""
    try:
        from config import PAUSE_TIMER_COMMANDS, RESUME_TIMER_COMMANDS
        from utils import is_command_match

        # Регулярное выражение для извлечения номера таймера
        if LANGUAGE == "en":
            match = re.search(r"(pause|stop|resume|continue|start) (\d+|[a-z]+)[^\d]*timer", command)
            # Альтернативный вариант: "timer X stop/pause"
            if not match:
                alt_match = re.search(r"timer (\d+|[a-z]+)[^\d]* (pause|stop|resume|continue|start)", command)
                if alt_match:
                    # Создаем новый паттерн поиска, где действие и номер поменяны местами
                    action = alt_match.group(2)
                    number = alt_match.group(1)
                    # Теперь ищем по новому паттерну, где действие идет первым
                    match = re.search(f"{action} {number}", f"{action} {number} timer")
            words_dict = number_words["en"]
        else:
            match = re.search(r"(останови|пауза|приостанови|продолжи|возобнови|запусти|стоп) (\d+|[а-я]+)[^\d]*таймер",
                              command)
            # Альтернативный вариант: "таймер X стоп/пауза"
            if not match:
                alt_match = re.search(
                    r"таймер (\d+|[а-я]+)[^\d]* (останови|пауза|приостанови|продолжи|возобнови|запусти|стоп)", command)
                if alt_match:
                    # Создаем новый паттерн поиска, где действие и номер поменяны местами
                    action = alt_match.group(2)
                    number = alt_match.group(1)
                    # Теперь ищем по новому паттерну, где действие идет первым
                    match = re.search(f"{action} {number}", f"{action} {number} таймер")
            words_dict = number_words["ru"]

        if match:
            number_str = match.group(2)
            timer_number = int(number_str) if number_str.isdigit() else words_dict.get(number_str, None)

            if timer_number:
                if pause_timer_by_number(timer_number):
                    if LANGUAGE == "en":
                        speak(f"Timer {timer_number} paused/resumed")
                    else:
                        speak(f"Таймер {timer_number} приостановлен/возобновлен")
                else:
                    if LANGUAGE == "en":
                        speak(f"Could not find timer {timer_number}")
                    else:
                        speak(f"Не удалось найти таймер {timer_number}")
            else:
                if LANGUAGE == "en":
                    speak("Could not determine timer number")
                else:
                    speak("Не удалось определить номер таймера")
        else:
            if LANGUAGE == "en":
                speak("Please specify which timer to pause or resume")
            else:
                speak("Укажите, какой именно таймер приостановить или возобновить")
    except Exception as e:
        if LANGUAGE == "en":
            print(f"Error processing pause/resume command: {e}")
            speak("An error occurred while pausing/resuming the timer")
        else:
            print(f"Ошибка при обработке команды паузы/возобновления: {e}")
            speak("Произошла ошибка при паузе/возобновлении таймера")
