import json
from Houssing import Houssing
from Weather import weather
from state import channel_data

class LLM_LLaMa_Local:
    def __init__(self, model):
        self.model = model
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

               
                {"role": "user", "content": "je cherche un logement"},
                {"role": "assistant", "content": '{"output":"logement"}'},

                {"role": "user", "content": "je cherche un hôtel"},
                {"role": "assistant", "content": '{"output":"logement"}'},

                {"role": "user", "content": "trouve moi un hôtel à Paris"},
                {"role": "assistant", "content": '{"output":"logement","city":"Paris"}'},

                {"role": "user", "content": "hôtel à Lyon"},
                {"role": "assistant", "content": '{"output":"logement","city":"Lyon"}'},

                {"role": "user", "content": "je veux dormir quelque part à Bordeaux"},
                {"role": "assistant", "content": '{"output":"logement","city":"Bordeaux"}'},

                {"role": "user", "content": "où dormir à Marseille"},
                {"role": "assistant", "content": '{"output":"logement","city":"Marseille"}'},

                {"role": "user", "content": "je veux un hôtel pas cher à Lille"},
                {"role": "assistant", "content": '{"output":"logement","city":"Lille"}'},

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
            data = channel_data.setdefault(channel_id, {
                "city": None
            })

            if output.get("city"):
                data["city"] = output["city"]

            # Cas 1 : il manque la ville
            if not data["city"]:
                return {
                    "tool": "logement",
                    "message": "Dans quelle ville cherchez-vous un hôtel ?"
                }

            # Cas 2 : ville connue → recherche
            city = data["city"]
            results = Houssing(city, "hotel").search()

            msg = f"Voici des hôtels à {city}\n\n"
            msg += "\n\n".join([f"**{r['titre']}** — {r['prix']}\n{r['url']}" for r in results])

            # Reset
            data["city"] = None

            return {
                "tool": "logement_done",
                "message": msg
            }