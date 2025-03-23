import re
import time

import keyboard
import pyautogui
import pygetwindow as gw
import requests


def is_command_match(command, command_list):
    """
    Проверяет соответствие команды одному из списка ключевых фраз.
    
    Args:
        command (str): Обрабатываемая команда
        command_list (list): Список ключевых фраз
        
    Returns:
        bool: True если команда соответствует одной из ключевых фраз
    """
    for cmd in command_list:
        if cmd in command:
            return True
    return False


def parse_time(command):
    try:
        time_parts = re.findall(r"(\d+)\s*(час[а-я]*|минут[а-я]*|секунд[а-я]*)?", command)
        total_seconds = 0

        for value, unit in time_parts:
            value = int(value)
            if not unit or unit.strip() == "":
                total_seconds += value * 60
            elif "час" in unit:
                total_seconds += value * 3600
            elif "минут" in unit or "минута" in unit:
                total_seconds += value * 60
            elif "секунд" in unit or "секунда" in unit:
                total_seconds += value

        return total_seconds if total_seconds > 0 else None
    except ValueError:
        return None


def check_internet():
    """ Проверяет наличие интернета, делая запрос к Google. """
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False


def toggle_radio():
    """
    Улучшенная функция для переключения на окно Chrome и запуска радио.
    Обрабатывает различные сценарии: несколько окон Chrome, свернутые окна,
    Chrome запущен в фоне, и другие краевые случаи.
    """
    MAX_ATTEMPTS = 3  # Максимальное количество попыток

    def try_click_radio(attempt=1):
        # Определяем текущее разрешение экрана
        screen_width, screen_height = pyautogui.size()

        # Вычисляем координаты кнопки в зависимости от разрешения
        x_rel, y_rel = 0.435, 0.156
        x_pos = int(screen_width * x_rel)
        y_pos = int(screen_height * y_rel)

        # Выполняем клик
        pyautogui.click(x_pos, y_pos)
        print(f"Выполнен клик по координатам ({x_pos}, {y_pos}) на экране {screen_width}x{screen_height}")

    # Проверка, запущен ли Chrome
    def is_chrome_running():
        try:
            chrome_windows = gw.getWindowsWithTitle("Chrome")
            return len(chrome_windows) > 0
        except Exception as e:
            print(f"Ошибка при проверке запущенного Chrome: {e}")
            return False

    # Закрываем меню Пуск и другие возможные элементы интерфейса
    def close_system_ui():
        try:
            print("Закрываем меню Пуск и другие элементы интерфейса...")
            # Нажимаем Escape для закрытия меню Пуск
            pyautogui.press('esc')
            time.sleep(0.2)

            pyautogui.press('esc')
            time.sleep(0.2)

            return True
        except Exception as e:
            print(f"Ошибка при закрытии системного интерфейса: {e}")
            return False

    # Попытка активировать окно Chrome
    def activate_chrome_window(attempt=1):
        if attempt > MAX_ATTEMPTS:
            print(f"Превышено максимальное количество попыток ({MAX_ATTEMPTS})")
            return False

        try:
            chrome_windows = gw.getWindowsWithTitle("Chrome")

            if not chrome_windows:
                print(f"Chrome не найден (попытка {attempt})")
                return False

            # Пробуем найти неминимизированное окно Chrome
            visible_windows = [win for win in chrome_windows if not win.isMinimized]

            if visible_windows:
                target_window = visible_windows[0]
                print(f"Найдено видимое окно Chrome: {target_window.title}")
            else:
                # Если все окна свернуты, восстанавливаем первое
                target_window = chrome_windows[0]
                print(f"Все окна Chrome свернуты. Восстанавливаем: {target_window.title}")
                if target_window.isMinimized:
                    target_window.restore()
                    time.sleep(0.5)

            # Переводим окно на передний план и активируем
            target_window.activate()
            time.sleep(0.5)  # Увеличиваем задержку до 1 секунды для надежности

            # Еще один метод активации - использование оконного менеджера Windows
            try:
                # Альтернативный способ фокусировки на окно
                target_window.moveTo(0, 0)  # Перемещаем окно в левый верхний угол
                time.sleep(0.5)
                target_window.activate()  # Активируем еще раз после перемещения
                time.sleep(0.5)
            except Exception as e:
                print(f"Дополнительная активация не удалась: {e}")

            # Проверяем, что окно действительно активно
            time.sleep(0.5)
            active_window = gw.getActiveWindow()

            if active_window and "Chrome" in active_window.title:
                print(f"Chrome успешно активирован: {active_window.title}")
                return True
            else:
                print(f"Не удалось активировать Chrome (попытка {attempt})")

                # Пробуем Alt+Tab для переключения между окнами
                pyautogui.keyDown('alt')
                for _ in range(3):  # Попробуем нажать Tab несколько раз
                    pyautogui.press('tab')
                    time.sleep(0.2)
                pyautogui.keyUp('alt')
                time.sleep(1.0)

                # Попробуем еще один способ - Win+Tab
                pyautogui.keyDown('win')
                pyautogui.press('tab')
                pyautogui.keyUp('win')
                time.sleep(0.5)

                # Пробуем кликнуть по центру экрана, где может быть Chrome
                screen_width, screen_height = pyautogui.size()
                pyautogui.click(screen_width // 2, screen_height // 2)
                time.sleep(0.5)

                return activate_chrome_window(attempt + 1)

        except Exception as e:
            print(f"Ошибка при активации Chrome (попытка {attempt}): {e}")
            return activate_chrome_window(attempt + 1) if attempt < MAX_ATTEMPTS else False

    # Запуск Chrome, если не запущен
    def launch_chrome():
        try:
            print("Запускаем Chrome...")

            # Закрываем меню Пуск, если оно открыто
            close_system_ui()

            # Вариант 1: через поиск Windows (Win + S)
            keyboard.press_and_release('win+s')
            time.sleep(1.0)  # Увеличиваем задержку
            keyboard.write('chrome')
            time.sleep(0.7)  # Увеличиваем задержку
            keyboard.press_and_release('enter')
            time.sleep(1.0)  # Даем больше времени на запуск

            # Ждем запуска Chrome
            for i in range(12):  # Ждем до 6 секунд
                time.sleep(0.5)
                if is_chrome_running():
                    print(f"Chrome запущен после {i / 2} секунд ожидания")
                    return True

        except Exception as e:
            print(f"Ошибка при запуске Chrome: {e}")
            return False

    print("Начинаем процесс запуска радио...")

    # Сначала попробуем закрыть все возможные системные окна
    close_system_ui()

    # Основной код функции
    if is_chrome_running():
        print("Chrome уже запущен")
        if activate_chrome_window():
            # Переключаемся на первую вкладку
            pyautogui.hotkey("ctrl", "1")
            time.sleep(1.0)  # Увеличиваем задержку
            try_click_radio()
            return True
    else:
        print("Chrome не запущен, пытаемся запустить")
        # Chrome не запущен, запускаем
        if launch_chrome() and activate_chrome_window():
            # Переключаемся на первую вкладку
            pyautogui.hotkey("ctrl", "1")
            time.sleep(1.0)  # Увеличиваем задержку
            try_click_radio()
            return True

    print("Не удалось открыть радио")
    return False
