import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Houssing:
    """
    A simple wrapper around the SerpAPI Google Hotels search engine.

    This class allows searching for hotel accommodations in a given city
    with optional price filtering.

    Attributes:
        city (str): The city or location to search hotels in.
        logement_type (str): Type of accommodation (currently unused in API query).
        api_token (str): API key for SerpAPI.
        price_min (int, optional): Minimum price per night filter (EUR).
        price_max (int, optional): Maximum price per night filter (EUR).
    """
    def __init__(self, city, logement_type, price_min=None, price_max=None):
        """
    Initialize a new Houssing search instance.

    Args:
        city (str): Destination city for hotel search.
        logement_type (str): Type of lodging (not currently used in query).
        api_token (str): SerpAPI API key.
        price_min (int, optional): Minimum nightly price in EUR.
        price_max (int, optional): Maximum nightly price in EUR.
    """
        self.city = city
        self.logement_type = logement_type
        self.price_min = price_min
        self.price_max = price_max
        self.api_token = os.getenv("SerpAPI")

    def search(self):
        """
        Search for hotels in the specified city using SerpAPI (Google Hotels engine).

        The method performs a request for a 1-night stay (today to tomorrow),
        retrieves hotel results, and filters them based on price constraints.

        Returns:
            list[dict]: A list of up to 3 hotels matching the criteria.
                Each dictionary contains:
                    - "titre" (str): Hotel name
                    - "prix" (int): Lowest price per night in EUR
                    - "url" (str): Link to the hotel page

        Notes:
            - Only results with a valid price are included.
            - Prices are normalized from strings like "€120" to integers.
            - The result list is limited to 3 entries.
        """
        today = datetime.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        response = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_hotels",
                "q": self.city,
                "check_in_date": today,
                "check_out_date": tomorrow,
                "api_key": self.api_token,
                "currency": "EUR",
                "hl": "fr",
                "gl": "fr"
            }
        )

        data = response.json()
        print(data.keys()) 

        results = []

        for item in data.get("properties", []):
            prix = item.get("rate_per_night", {}).get("lowest")

            if prix is None:
                continue

            if isinstance(prix, str):
                prix = int(prix.replace("€", "").strip())

            if self.price_min is not None and prix < self.price_min:
                continue

            if self.price_max is not None and prix > self.price_max:
                continue

            results.append({
                "titre": item.get("name", "Hôtel"),
                "prix": prix,
                "url": item.get("link", "")
            })

            if len(results) == 3:
                break

        return results