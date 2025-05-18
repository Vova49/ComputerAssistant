import time

from command_handlers import (
    process_greeting_command, process_time_command, process_thanks_command,
    process_system_command, process_music_command, process_radio_command,
    process_weather_command, process_calculator_command
)
from config import (
    TIME_COMMANDS, WEATHER_COMMANDS,
    RADIO_ON_COMMANDS, RADIO_OFF_COMMANDS, LANGUAGE, CALCULATOR_COMMANDS
)
from language_manager import (
    get_message, get_commands
)
from speech_recognition_manager import (
    handle_speech_recognition, check_microphone, wait_for_microphone
)
from timer_manager import update_timer_ui, process_timer_command
from utils import check_internet, is_command_match


def main():
    # Ожидаем появления микрофона перед началом работы
    wait_for_microphone()

    print(get_message("assistant_active"))

    while True:
        try:
            # Проверяем очередь на наличие обновлений UI
            update_timer_ui()

            # Проверяем подключение к интернету
            if not check_internet():
                print(get_message("no_internet"))
                time.sleep(5)
                continue

            # Проверяем микрофон
            if not check_microphone():
                print(get_message("microphone_disconnected"))
                wait_for_microphone()
                continue

            command = handle_speech_recognition()
            if not command:
                continue

            # Получаем актуальные команды в зависимости от языка
            greeting_commands = get_commands("GREETING_COMMANDS")
            thanks_commands = get_commands("THANKS_COMMANDS")
            shutdown_commands = get_commands("SHUTDOWN_COMMANDS")
            music_on_commands = get_commands("MUSIC_ON_COMMANDS")
            music_off_commands = get_commands("MUSIC_OFF_COMMANDS")
            pause_timer_commands = get_commands("PAUSE_TIMER_COMMANDS")
            resume_timer_commands = get_commands("RESUME_TIMER_COMMANDS")

            # Обработка команд
            if any(greeting in command for greeting in greeting_commands):
                process_greeting_command()
            elif is_command_match(command, TIME_COMMANDS):
                process_time_command()
            elif any(thanks in command for thanks in thanks_commands):
                process_thanks_command()

            # Системные команды
            elif any(shutdown in command for shutdown in shutdown_commands):
                process_system_command(command)

            # Управление таймерами
            elif "timer" in command and LANGUAGE == "en" or "таймер" in command and LANGUAGE == "ru":
                # Явно проверяем отдельные ключевые слова для приостановки/возобновления таймера
                pause_keywords_ru = ["останови", "пауза", "приостанови", "стоп"]
                resume_keywords_ru = ["продолжи", "возобнови", "запусти"]
                pause_keywords_en = ["pause", "stop", "hold"]
                resume_keywords_en = ["resume", "continue", "start"]

                # Проверяем наличие ключевых слов в команде
                command_words = command.lower().split()
                if LANGUAGE == "en":
                    has_pause_keyword = any(word in command_words for word in pause_keywords_en)
                    has_resume_keyword = any(word in command_words for word in resume_keywords_en)
                else:
                    has_pause_keyword = any(word in command_words for word in pause_keywords_ru)
                    has_resume_keyword = any(word in command_words for word in resume_keywords_ru)

                # Проверяем, является ли команда командой управления таймером
                if has_pause_keyword or has_resume_keyword:
                    from timer_manager import process_pause_resume_timer_command
                    process_pause_resume_timer_command(command)
                else:
                    process_timer_command(command)

            # Управление музыкой
            elif any(music_cmd in command for music_cmd in music_on_commands + music_off_commands):
                process_music_command(command)

            # Управление радио
            elif is_command_match(command, RADIO_ON_COMMANDS) or is_command_match(command, RADIO_OFF_COMMANDS):
                process_radio_command(command, RADIO_ON_COMMANDS, RADIO_OFF_COMMANDS)

            # Погода
            elif is_command_match(command, WEATHER_COMMANDS):
                process_weather_command()

            # Калькулятор
            elif is_command_match(command, CALCULATOR_COMMANDS):
                process_calculator_command()

            else:
                print(get_message("not_understood"))

        except Exception as e:
            print(get_message("error_occurred", e))
            try:
                from audio_manager import speak
                speak(get_message("unknown_error"))
            except:
                print("Не удалось вывести голосовое сообщение об ошибке")


if __name__ == "__main__":
    from audio_manager import set_volume
    from config import DEFAULT_VOLUME

    set_volume(DEFAULT_VOLUME)
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + get_message("program_terminated"))
    except Exception as e:
        print(get_message("critical_error", e))
