import time

from command_handlers import (
    process_greeting_command, process_time_command, process_thanks_command,
    process_system_command, process_music_command, process_radio_command,
    process_weather_command
)
from config import (
    TIME_COMMANDS, WEATHER_COMMANDS,
    RADIO_ON_COMMANDS, RADIO_OFF_COMMANDS
)
from speech_recognition_manager import (
    handle_speech_recognition, check_microphone, wait_for_microphone
)
from timer_manager import update_timer_ui, process_timer_command
from utils import check_internet, is_command_match
from video_manager import process_video_command


def main():
    # Ожидаем появления микрофона перед началом работы
    wait_for_microphone()

    print("Ассистент активен")

    while True:
        try:
            # Проверяем очередь на наличие обновлений UI
            update_timer_ui()

            # Проверяем подключение к интернету
            if not check_internet():
                print("Интернет отсутствует, жду подключения...")
                time.sleep(5)
                continue

            # Проверяем микрофон
            if not check_microphone():
                print("Микрофон был отключен. Ожидание...")
                wait_for_microphone()
                continue

            command = handle_speech_recognition()
            if not command:
                continue

            # Обработка команд
            if "привет" in command:
                process_greeting_command()
            elif is_command_match(command, TIME_COMMANDS):
                process_time_command()
            elif "спасибо" in command or "благодарю" in command:
                process_thanks_command()

            # Системные команды
            elif "выключи компьютер" in command:
                process_system_command(command)

            # Управление таймерами
            elif "таймер" in command:
                process_timer_command(command)

            # Управление музыкой
            elif "музыку" in command:
                process_music_command(command)

            # Управление радио
            elif is_command_match(command, RADIO_ON_COMMANDS) or is_command_match(command, RADIO_OFF_COMMANDS):
                process_radio_command(command, RADIO_ON_COMMANDS, RADIO_OFF_COMMANDS)

            # Погода
            elif is_command_match(command, WEATHER_COMMANDS):
                process_weather_command()

            # Воспроизведение видео
            elif "включи" in command:
                process_video_command(command)

            else:
                print("Я вас не понял. Попробуйте снова.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            try:
                from audio_manager import speak
                speak("Произошла неизвестная ошибка. Попробуйте снова.")
            except:
                print("Не удалось вывести голосовое сообщение об ошибке")


if __name__ == "__main__":
    from audio_manager import set_volume
    from config import DEFAULT_VOLUME

    set_volume(DEFAULT_VOLUME)
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
