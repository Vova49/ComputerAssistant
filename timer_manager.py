import queue
import re
import threading
import tkinter as tk
from datetime import datetime, timedelta

from audio_manager import set_volume, play_sound, speak
from config import TIMER_VOLUME, TIMER_WINDOW_WIDTH, TIMER_WINDOW_HEIGHT

timer_threads = []
timer_windows = []
next_timer_number = 1
timer_queue = queue.Queue()
# Добавляем мьютекс для синхронизации доступа к общим ресурсам
timer_lock = threading.Lock()

number_words = {
    "первый": 1, "второй": 2, "третий": 3, "четвертый": 4, "пятый": 5,
    "шестой": 6, "седьмой": 7, "восьмой": 8, "девятый": 9, "десятый": 10,
    "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
    "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10
}


def process_timer_command(command):
    """Обрабатывает команды, связанные с таймерами."""
    from config import TIMER_COMMANDS, CLOSE_ALL_TIMERS_COMMANDS

    try:
        # Проверка команды "таймер на X минут"
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
                speak(f"Таймер поставлен.")
            else:
                speak("Не удалось определить время таймера")

        elif any(word in command for word in CLOSE_ALL_TIMERS_COMMANDS):
            close_all_timers()
            speak("Все таймеры выключены.")

        else:
            match = re.search(r"(закрой|выключи) (\d+|[а-я]+)[^\d]*таймер", command)
            if match:
                number_str = match.group(2)
                timer_number = int(number_str) if number_str.isdigit() else number_words.get(number_str, None)
                if timer_number:
                    if close_timer_by_number(timer_number):
                        speak(f"Таймер {timer_number} закрыт")
                    else:
                        speak(f"Не удалось закрыть таймер {timer_number}")
                else:
                    speak("Не удалось определить номер таймера.")
    except Exception as e:
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
                    _, window, _, _ = timer
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
                old_number, window, stop_event, set_force_stop = timer
                if old_number != i:
                    print(f"Обновление номера таймера с {old_number} на {i}")
                    try:
                        timer_queue.put((window, i))
                    except Exception as e:
                        print(f"Ошибка при обновлении номера таймера: {e}")
                new_timer_windows.append((i, window, stop_event, set_force_stop))

            timer_windows.clear()
            timer_windows.extend(new_timer_windows)

            next_timer_number = len(timer_windows) + 1
    except Exception as e:
        print(f"Ошибка при обновлении номеров таймеров: {e}")


def create_circular_timer(seconds):
    global next_timer_number
    try:
        print(f"Создание нового таймера на {seconds} секунд")
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=seconds)
        end_time_str = end_time.strftime("%H:%M")

        def update_timer():
            nonlocal seconds, force_stop
            # Убираем обращение к глобальной переменной total_seconds
            nonlocal total_seconds
            try:
                if seconds >= 0 and not stop_event.is_set():
                    canvas.delete("all")
                    draw_timer(seconds)
                    seconds -= 1
                    root.after(1000, update_timer)
                else:
                    if not force_stop:
                        set_volume(TIMER_VOLUME)
                        play_sound()
                    root.after(3000, root.quit)
            except Exception as e:
                print(f"Ошибка в update_timer: {e}")
                root.quit()

        def draw_timer(time_left):
            try:
                # Используем локальную переменную total_seconds
                nonlocal total_seconds
                canvas.create_oval(30, 30, 270, 270, outline="black", width=9)
                hours, remainder = divmod(time_left, 3600)
                minutes, secs = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{secs:02}" if hours > 0 else f"{minutes:02}:{secs:02}"

                # Уменьшаем размер шрифта, если отображаются часы
                font_size = 40 if hours == 0 else 30

                canvas.create_text(150, 130, text=time_str, font=("Arial", font_size, "bold"), fill="red")

                angle = -((time_left / total_seconds) * 360)
                canvas.create_arc(30, 30, 270, 270, start=90, extent=angle, outline="red", width=10, style=tk.ARC)

                canvas.create_text(150, 180, text=f"Закончится в {end_time_str}", font=("Arial", 14), fill="black")
            except Exception as e:
                print(f"Ошибка в draw_timer: {e}")

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
                print(f"Ошибка при закрытии таймера: {e}")

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

        label = tk.Label(root, text=f"Таймер {timer_number}", font=("Arial", 12, "bold"), bg="white")
        label.pack()

        canvas = tk.Canvas(root, width=TIMER_WINDOW_WIDTH, height=TIMER_WINDOW_HEIGHT - 15, bg="white")
        canvas.pack()

        canvas.bind("<ButtonPress-1>", start_move)
        canvas.bind("<B1-Motion>", move_window)

        # Создаем локальную переменную total_seconds вместо глобальной
        total_seconds = seconds

        stop_event = threading.Event()
        force_stop = False

        # Добавление таймера в список с синхронизацией
        with timer_lock:
            timer_windows.append((timer_number, root, stop_event, lambda: set_force_stop()))

        def set_force_stop():
            nonlocal force_stop
            force_stop = True

        update_timer()
        root.mainloop()
        stop_event.set()
    except Exception as e:
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

            _, window, stop_event, set_force_stop = timer_to_close
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
                    _, window, stop_event, set_force_stop = timer
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
