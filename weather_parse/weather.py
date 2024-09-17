import requests
from .secret import OPEN_WEATHER_API_KEY

def get_weather(location: str):
    if location:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPEN_WEATHER_API_KEY}&units=metric'
        response = requests.get(url)
        data = response.json()
        answer_dict = {'country': data['sys']['country'],
                       'temp_max': data['main']['temp_max'],
                       'temp_min': data['main']['temp_min'],
                       'description': data['weather'][0]['description']}
        return answer_dict
