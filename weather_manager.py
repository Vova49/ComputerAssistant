import requests

from config import WEATHER_API_KEY, DEFAULT_CITY


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

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            return f"Сейчас в {city}: {temp} градусов, {weather}"
        else:
            return f"Ошибка: {data.get('message', 'Не удалось получить данные')}"
    except requests.ConnectionError:
        return "Не удалось получить погоду. Проверьте подключение к интернету."
    except Exception as e:
        return f"Ошибка запроса: {e}"
