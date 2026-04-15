import json
from Houssing import Houssing
from Weather import weather
from state import channel_data
from Transport_by import search_trains

class LLM_LLaMa_Local:
    def __init__(self, model,serp_api_key):
        self.model = model
        self.SerpAPI = serp_api_key
        self.contexts = {}
        self.system_prompt = [{
            "role": "system",
            "content": "Tu es un assistant serviable. Réponds TOUJOURS en français, peu importe la langue de l'utilisateur."
        }]

    def context(self, channel_id):
        if len(self.contexts[channel_id]) > 20:
            self.contexts[channel_id] = list(self.system_prompt) + self.contexts[channel_id][-20:]

    def classify(self, message: str):
        result = self.model.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a classifier. Output ONLY raw JSON. No text, no explanation.\n"
                        "Possible outputs:\n"
                        '{"output":"weather","city":"CITY","days":N,"hour":H or null}\n'
                        '{"output":"train","from":"CITY","to":"CITY","days":N,"hour":H or null}\n'
                        '{"output":"logement","city":"CITY","price_min":N or null,"price_max":N or null}\n'
                        '{"output":"other"}'
                    )
                },

               # Examples for Houssing
                {"role": "user", "content": "hôtel à Paris"},
                {"role": "assistant", "content": '{"output":"logement","city":"Paris"}'},
                {"role": "user", "content": "hôtel pas cher à Lille"},
                {"role": "assistant", "content": '{"output":"logement","city":"Lille","price_max":80}'},
                {"role": "user", "content": "moins de 100€ à Lyon"},
                {"role": "assistant", "content": '{"output":"logement","city":"Lyon","price_max":100}'},
                {"role": "user", "content": "entre 80 et 150€ à Nice"},
                {"role": "assistant", "content": '{"output":"logement","city":"Nice","price_min":80,"price_max":150}'},
                {"role": "user", "content": "je veux un hôtel à Marseille"},
                {"role": "assistant", "content": '{"output":"logement","city":"Marseille"}'},

                # Examples for météo
                {"role": "user", "content": "météo à Paris ?"},
                {"role": "assistant", "content": '{"output":"weather","city":"Paris","days":0}'},
                {"role": "user", "content": "température à Lyon demain"},
                {"role": "assistant", "content": '{"output":"weather","city":"Lyon","days":1}'},
                {"role": "user", "content": "il fait chaud à Nantes dans 2 jours ?"},
                {"role": "assistant", "content": '{"output":"weather","city":"Nantes","days":2}'},

                # Examples if no functions needed
                {"role": "user", "content": "raconte moi une blague"},
                {"role": "assistant", "content": '{"output":"other"}'},
                {"role": "user", "content": "c'est quoi la capitale de l'Espagne ?"},
                {"role": "assistant", "content": '{"output":"other"}'},

                # Examples for SNCF trains
                {"role": "user", "content": "train de Paris à Lyon ?"},
                {"role": "assistant", "content": '{"output":"train","from":"Paris","to":"Lyon","days":0}'},
                {"role": "user", "content": "horaires Nantes Vannes demain"},
                {"role": "assistant", "content": '{"output":"train","from":"Nantes","to":"Vannes","days":1}'},
                {"role": "user", "content": "je veux aller à Bordeaux depuis Paris dans 2 jours"},
                {"role": "assistant", "content": '{"output":"train","from":"Paris","to":"Bordeaux","days":2}'},
                
                # Example for hour:
                {"role": "user", "content": "train Nantes Vannes demain à 15h"},
                {"role": "assistant", "content": '{"output":"train","from":"Nantes","to":"Vannes","days":1,"hour":15}'},
                {"role": "user", "content": "horaires Paris Lyon à 9h"},
                {"role": "assistant", "content": '{"output":"train","from":"Paris","to":"Lyon","days":0,"hour":9}'},

                # Real message we asking for:
                {"role": "user", "content": message}
            ],
            max_tokens=50
        )

        response = result["choices"][0]["message"]["content"].strip()

        try:
            return json.loads(response)
        except:
            return {"output": "other"}

    def get_llm_response(self, user_message, channel_id):

        if channel_id not in self.contexts:
            self.contexts[channel_id] = list(self.system_prompt)

        self.contexts[channel_id].append({"role": "user", "content": user_message})

        output = self.classify(user_message)

        if output.get("output") == "weather":
            city = output.get("city")
            days = int(output.get("days", 0))
            print(f"weather reconnu : city={city}, days={days}")

            results_weather = weather(city, days)

            reform = self.model.create_chat_completion(messages=[
                {"role": "system", "content": "Tu es un assistant météo. Réponds UNIQUEMENT en français en une seule phrase courte."},
                {"role": "user", "content": "A Paris: 22°C"},
                {"role": "assistant", "content": "Il fait actuellement 22°C à Paris."},
                {"role": "user", "content": "A Bordeaux: Minimum température : 8, Maximum température : 15"},
                {"role": "assistant", "content": "À Bordeaux, les températures seront comprises entre 8°C et 15°C."},
                # Real message we asking for :
                {"role": "user", "content": str(results_weather)}
            ])

            final_response = reform["choices"][0]["message"]["content"]

            self.contexts[channel_id].append({"role": "assistant", "content": final_response})
            self.context(channel_id)
            return final_response

        # if transportation asked by user :
        if output.get("output") == "train":
            from_city = output.get("from")
            to_city = output.get("to")
            days = int(output.get("days", 0))
            hour = output.get("hour")
            if hour:
                hour = int(hour)

            print(f"train reconnu : ville départ ={from_city}, ville arrivée={to_city}, days={days}, heure={hour}")

            results_train = search_trains(from_city, to_city, days, hour)

            reform = self.model.create_chat_completion(messages=[
                {"role": "system", "content": "Tu es un assistant transport. Reformule ces horaires de train en français de façon claire et concise."},
                {"role": "user", "content": "Départ: 15/04 à 08h12 → Arrivée: 09h45 (93 min)\nDépart: 15/04 à 10h00 → Arrivée: 11h30 (90 min)"},
                {"role": "assistant", "content": "Voici les prochains trains : départ à 8h12 (arrivée 9h45) ou à 10h00 (arrivée 11h30), comptez environ 1h30 de trajet."},
                # Real message we asking for :
                {"role": "user", "content": str(results_train)}
            ])
            final_response = reform["choices"][0]["message"]["content"]
            self.contexts[channel_id].append({"role": "assistant", "content": final_response})
            self.context(channel_id)
            return final_response

        # if houssing asked by user :
        if output.get("output") == "logement":
            data = channel_data.setdefault(channel_id, {})

            data.setdefault("city", None)
            data.setdefault("price_min", None)
            data.setdefault("price_max", None)

            user_text = user_message.lower()

        
            no_budget = any(x in user_text for x in [
                "pas de budget",
                "sans budget",
                "aucun budget",
                "je n'ai pas de budget",
                "peu importe"
            ])

        
            if output.get("city"):
                if data["city"] and data["city"] != output["city"]:
                    data["price_min"] = None
                    data["price_max"] = None

                data["city"] = output["city"]

            if output.get("price_min") is not None:
                data["price_min"] = output["price_min"]

            if output.get("price_max") is not None:
                data["price_max"] = output["price_max"]

            if not data["city"]:
                return {
                    "tool": "logement",
                    "message": "Dans quelle ville cherchez-vous un logement ?"
                }

        
            if not no_budget:
                if data["price_min"] is None and data["price_max"] is None:
                    return {
                        "tool": "logement",
                        "message": "Vous avez un budget minimum ou maximum ?"
                    }

            if no_budget:
                data["price_min"] = None
                data["price_max"] = None


            city = data["city"]
            price_min = data["price_min"]
            price_max = data["price_max"]

            results = Houssing(city, "hotel", self.SerpAPI, price_min, price_max).search()
            if not results:
                return {
                    "tool": "logement_done",
                    "message": f"Aucun logement trouvé à {city} avec les critères spécifiés."
                }

            msg = f"Voici des logements à {city}"

            if price_min is not None or price_max is not None:
                msg += " ("
                if price_min is not None:
                    msg += f"min {price_min}€"
                if price_min is not None and price_max is not None:
                    msg += " - "
                if price_max is not None:
                    msg += f"max {price_max}€"
                msg += ")"

            msg += "\n\n"

            msg += "\n\n".join([
                f"**{r['titre']}** — {r['prix']}€\n{r['url']}"
                for r in results
            ])

            return {
                "tool": "logement_done",
                "message": msg 
            }
        
        # No weather/train asked by user
        result = self.model.create_chat_completion(
            messages=self.contexts[channel_id],
            max_tokens=300
        )
        response = result["choices"][0]["message"]["content"]
        self.contexts[channel_id].append({"role": "assistant", "content": response})
        self.context(channel_id)
        return response