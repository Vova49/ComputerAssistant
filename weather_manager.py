import requests

from config import WEATHER_API_KEY, DEFAULT_CITY, LANGUAGE


def get_current_weather(city=None):
    """
    Получает текущую погоду в городе.
    
    Args:
        city (str, optional): Название города. По умолчанию используется город из конфигурации.
    
    Returns:
        str: Строка с информацией о погоде
    """
    if city is None:
        city = DEFAULT_CITY

    # Выбираем язык для API
    lang = "en" if LANGUAGE == "en" else "ru"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang={lang}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]

            if LANGUAGE == "en":
                return f"Currently in {city}: {temp} degrees, {weather}"
            else:
                return f"Сейчас в {city}: {temp} градусов, {weather}"
        else:
            if LANGUAGE == "en":
                return f"Error: {data.get('message', 'Failed to get data')}"
            else:
                return f"Ошибка: {data.get('message', 'Не удалось получить данные')}"
    except requests.ConnectionError:
        if LANGUAGE == "en":
            return "Could not get weather information. Check your internet connection."
        else:
            return "Не удалось получить погоду. Проверьте подключение к интернету."
    except Exception as e:
        if LANGUAGE == "en":
            return f"Request error: {e}"
        else:
            return f"Ошибка запроса: {e}"
