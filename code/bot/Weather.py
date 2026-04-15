import requests
import os
from dotenv import load_dotenv


"""
Function weather to get informations from API

This function retrieves current or forecast weather data for a given city.
It also handles API errors and invalid city names.

- If days == 0 it returns current temperature.
- If days > 0 it returns minimum and maximum forecast temperature.

city has to be string and days needs to be integer.

The response is given in French even if it's an error.
"""


load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def weather(city, days=0):
    
    if days == 0:
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
        
        res = requests.get(url)
        if res.status_code != 200:
            return "Erreur API Météo"
        data = res.json()
        if "error" in data:
            return "Aucune ville avec ce nom n'a été trouvé"
        
        temp_c = data['current']['temp_c']
        print(temp_c)
        return (f"A {city}: {temp_c}°C")
    else:
        url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days={days}&aqi=no&alerts=no"
        
        res = requests.get(url)
        if res.status_code != 200:
            return "Erreur API Météo"
        data = res.json()

        if "error" in data:
            return "Aucune ville avec ce nom n'a été trouvé"
        else:
            forecast_day_min_temp = data['forecast']['forecastday'][0]['day']['mintemp_c']
            forecast_day_max_temp = data['forecast']['forecastday'][0]['day']['maxtemp_c']
            # print(forecast_day_min_temp)
            # print(forecast_day_max_temp)
            return(f"A {city}: Température minimale prévue: {forecast_day_min_temp}, Température maximale prévue: {forecast_day_max_temp}")
