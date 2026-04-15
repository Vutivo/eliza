import json
from Houssing import Houssing
from Weather import weather
from state import channel_data

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
                        '{"output":"weather","city":"CITY","days":N} or '
                        '{"output":"logement"} or '
                        '{"output":"other"}'
                    )
                },

               # Examples for Houssing
                {"role": "user", "content": "hôtel à Paris"},
                {"role": "assistant", "content": "{\"output\":\"logement\",\"city\":\"Paris\"}"},
                {"role": "user", "content": "hôtel pas cher à Lille"},
                {"role": "assistant", "content": "{\"output\":\"logement\",\"city\":\"Lille\",\"price_max\":80}"},
                {"role": "user", "content": "moins de 100€ à Lyon"},
                {"role": "assistant", "content": "{\"output\":\"logement\",\"city\":\"Lyon\",\"price_max\":100}"},
                {"role": "user", "content": "entre 80 et 150€ à Nice"},
                {"role": "assistant", "content": "{\"output\":\"logement\",\"city\":\"Nice\",\"price_min\":80,\"price_max\":150}"},
                {"role": "user", "content": "je veux un hôtel à Marseille"},
                {"role": "assistant", "content": "{\"output\":\"logement\",\"city\":\"Marseille\"}"},
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

            results_weather = weather(city, days)

            reform = self.model.create_chat_completion(messages=[
                {"role": "system", "content": "Tu es un assistant météo. Réponds UNIQUEMENT en français en une seule phrase courte."},
                {"role": "user", "content": str(results_weather)}
            ])

            final_response = reform["choices"][0]["message"]["content"]

            self.contexts[channel_id].append({"role": "assistant", "content": final_response})
            self.context(channel_id)
            return final_response

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