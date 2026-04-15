import requests
from datetime import datetime, timedelta
from Chat_TPG import SerpAPI


class Houssing:
    def __init__(self, city, logement_type):
        self.city = city
        self.logement_type = logement_type
        self.api_token = SerpAPI

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
        for item in data.get("properties", [])[:3]:
            results.append({
                "titre": item.get("name", "Hôtel"),
                "prix": item.get("rate_per_night", {}).get("lowest", "?"),
                "url": item.get("link", "")
            })

        return results
