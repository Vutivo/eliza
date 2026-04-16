import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
SNCF_API_KEY = os.getenv("SNCF_API_KEY")

"""
Transport_by.py

This file is to give train journeys with the SNCF API.
Using : https://api.sncf.com/v1
"""

def get_place_id(city_name):
    """
    Look for a stop_area ID in Navitia
    
    city_name = Name of the city or of the train station
    
    This function return the Navitia place ID with the stop_area or an error is not found.
    """
    url = "https://api.sncf.com/v1/coverage/sncf/places"
    params = {"q": city_name, "type[]": "stop_area"}
    res = requests.get(url, auth=(SNCF_API_KEY, ""), params=params)
    data = res.json()

    places = data.get("places", [])
    if not places:
        return None, f"Gare '{city_name}' introuvable"
    
    # Takes only the 1st place
    place = places[0]
    print(f"Trouver : {city_name} -> {place['id']} ({place['name']})")
    return place["id"], None


def search_trains(from_city, to_city, days=0, hour=None):
    """
    Search for train between two cities using SNCF API.

    from_city is a string. It's the departure city.
    to_city is a string. It's the arrival city.
    days is an integer. It's the number of day from today,for example today is 0 and tomororrow is 1.
    hour is an integer. It's the hour of the day. If not provided, it's the current time for today and 8am for a forecast.

    This function return 3 journeys with : departure date, time and duration or an error if the city is not found.
    """

    from_id, err = get_place_id(from_city)
    if err:
        return err
    
    to_id, err = get_place_id(to_city)
    if err:
        return err

    # take the hour of the day
    target_date = datetime.now() + timedelta(days=days)
    if hour:
        datetime_str = target_date.strftime(f"%Y%m%dT{hour:02d}0000")  # d, to force integer
    elif days == 0:
        datetime_str = target_date.strftime("%Y%m%dT%H%M%S")  # heure actuelle
    else:
        datetime_str = target_date.strftime("%Y%m%dT080000")   # 8h par défaut

    url = "https://api.sncf.com/v1/coverage/sncf/journeys"
    params = {
        "from": from_id,
        "to": to_id,
        "datetime": datetime_str,
        "count": 3
    }
    res = requests.get(url, auth=(SNCF_API_KEY, ""), params=params)
    data = res.json()

    journeys = data.get("journeys", [])
    if not journeys:
        return f"Aucun trajet trouvé entre {from_city} et {to_city}."

    result = []
    for j in journeys:
        departure = j["departure_date_time"]
        arrival = j["arrival_date_time"]
        duration = j["duration"] // 60

        # from API:
        # year = [0:4]
        # month = [4:6]
        # days = [6:8]
        # hour = [9:11]
        # minute = [11:13]

        final_departure = f"{departure[6:8]}/{departure[4:6]} à {departure[9:11]}h{departure[11:13]}"
        final_arrival = f"{arrival[9:11]}h{arrival[11:13]}"

        result.append(f"Départ: {final_departure} → Arrivée: {final_arrival} ({duration} min)")

    return "\n".join(result)


# # Tests
# print(search_trains("Nantes", "Vannes"))                      # today
# print(search_trains("Nantes", "Paris", days=2))              # tomorrow, at 8
# print(search_trains("Nantes", "Vannes", days=1, hour=10))     # tomorrow, at 10