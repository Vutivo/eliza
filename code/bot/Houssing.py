import requests
from datetime import datetime, timedelta


class Houssing:
    def __init__(self, city, logement_type, api_token, price_min=None, price_max=None):
        self.city = city
        self.logement_type = logement_type
        self.price_min = price_min
        self.price_max = price_max
        self.api_token = api_token

    def search(self):
    
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