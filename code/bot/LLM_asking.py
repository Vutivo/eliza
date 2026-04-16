import json
from Houssing import Houssing
from Weather import weather
from Transport_by import search_trains


channel_data = {}

class LLM_LLaMa_Local:
    def __init__(self, model):
        self.model = model
        self.contexts = {}
        self.last_result = {}
        self.system_prompt = [{
            "role": "system",
            "content": "Tu es un assistant serviable. Réponds TOUJOURS en français, peu importe la langue de l'utilisateur."
        }]

    def context(self, channel_id):
        messages = self.contexts[channel_id]

        # keep last messages only
        if len(messages) > 4:
            messages = messages[-4:]

        # always ensure system prompt at start
        self.contexts[channel_id] = list(self.system_prompt) + messages

    def classify(self, message: str):
        result = self.model.create_chat_completion(
            messages=[{
                "role": "system",
                "content": (
                    "You are a strict JSON classifier.\n"
                    "Output ONLY valid JSON. No text. No markdown.\n"
                    "The output must be directly parsable by json.loads().\n"
                    "Use null for missing values.\n\n"
                    "Possible outputs:\n"
                    '{"output":"weather","city":"Paris","days":0,"hour":null}\n'
                    '{"output":"train","from":"Paris","to":"Lyon","days":1,"hour":15}\n'
                    '{"output":"logement","city":"Nantes","price_min":80,"price_max":120}\n'
                    '{"output":"other"}'
                )},

                # Example for houssing
                {"role": "user", "content": "hôtel entre 80 et 150€ à Nice"},
                {"role": "assistant", "content": '{"output":"logement","city":"Nice","price_min":80,"price_max":150}'},
                {"role": "user", "content": "je cherche un logement à Vannes pour 200 euros la nuit"},
                {"role": "assistant", "content": '{"output":"logement","city":"Vannes","price_min":null,"price_max":200}'},

                # Example for weather
                {"role": "user", "content": "météo à Paris demain"},
                {"role": "assistant", "content": '{"output":"weather","city":"Paris","days":1,"hour":null}'},

                # Example for train
                {"role": "user", "content": "train Nantes Lyon demain à 15h"},
                {"role": "assistant", "content": '{"output":"train","from":"Nantes","to":"Lyon","days":1,"hour":15}'},

                # Example for other
                {"role": "user", "content": "raconte moi une blague"},
                {"role": "assistant", "content": '{"output":"other"}'},

                # Real message
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0,
            response_format={"type": "json_object"}
        )

        response = result["choices"][0]["message"]["content"].strip()
        try:
            print(f"response: {response}")
            return json.loads(response)
        except:
            return {"output": "other"}

    def add_message(self, channel_id, role, message):
        self.contexts[channel_id].append({
            "role": role,
            "content": message
        })
        self.context(channel_id)

    def get_llm_response(self, user_message, channel_id):

        if channel_id not in self.contexts:
            self.contexts[channel_id] = list(self.system_prompt)

        self.contexts[channel_id].append({"role": "user", "content": user_message})

        output = self.classify(user_message)

        if output.get("output") == "weather":
            city = output.get("city")
            days = int(output.get("days") or 0)
            # print(f"weather reconnu : city={city}, days={days}")

            results_weather = weather(city, days)
            print(f"results_weather: {results_weather}")

            reform = self.model.create_chat_completion(messages=[
                {"role": "system", "content": "Tu es un assistant météo. Réponds UNIQUEMENT en français, sous forme de liste."},
                {"role": "user", "content": "A Paris: 22°C"},
                {
                    "role": "assistant",
                    "content": (
                        "Météo à Paris actuellement :\n"
                        "- Température → 22°C"
                    )
                },
                {"role": "user","content": "A Bordeaux: Température minimale prévue: 8.3, Température maximale prévue: 15.7, Dans 2 jours"},
                {
                    "role": "assistant",
                    "content": (
                        "Météo à Bordeaux dans 2 jours :\n"
                        "- Minimale → 8°C\n"
                        "- Maximale → 15°C"
                    )
                },
                {"role": "user", "content": str(results_weather)}
            ])

            final_response = reform["choices"][0]["message"]["content"]

            self.contexts[channel_id].append({"role": "assistant", "content": final_response})
            self.context(channel_id)

            result = {"type": "weather", "city": city, "days": days, "text": final_response}
            if channel_id not in self.last_result:
                self.last_result[channel_id] = {}
            self.last_result[channel_id]["weather"] = result

            return result

        # if transportation asked by user :
        if output.get("output") == "train":
            from_city = output.get("from")
            to_city = output.get("to")
            days = int(output.get("days") or 0)
            hour = output.get("hour")
            hour = int(hour) if hour is not None else None
            if hour:
                hour = int(hour)

            print(f"train reconnu : ville départ ={from_city}, ville arrivée={to_city}, days={days}, heure={hour}")

            results_train = search_trains(from_city, to_city, days, hour)

            reform = self.model.create_chat_completion(messages=[
                {
                    "role": "system",
                    "content": "Tu es un assistant transport. Reformule ces horaires de train en français de façon claire et concise. Réponds UNIQUEMENT en français."
                },
                {
                    "role": "user",
                    "content": "Départ: 15/04 à 08h12 → Arrivée: 09h45 (93 min)\nDépart: 15/04 à 10h00 → Arrivée: 11h30 (90 min)\nDépart: 15/04 à 13h00 → Arrivée: 14h45 (105 min)"
                },
                {
                    "role": "assistant",
                    "content": (
                        "Voici les prochains trains :\n"
                        "1. 08h12 → 09h45 — durée : 1h33\n"
                        "2. 10h00 → 11h30 — durée : 1h30\n"
                        "3. 13h00 → 14h45 — durée : 1h45"
                    )
                },
                {
                    "role": "user",
                    "content": str(results_train)
                }
            ])

            final_response = reform["choices"][0]["message"]["content"]
            self.contexts[channel_id].append({"role": "assistant", "content": final_response})
            self.context(channel_id)

            result = {"type": "train", "from": from_city, "to": to_city, "text": final_response}
            if channel_id not in self.last_result:
                self.last_result[channel_id] = {}

            self.last_result[channel_id]["train"] = result

            return result

        # if houssing asked by user :
        if output.get("output") == "logement":
            print("logement reconnu")
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
                message = "Dans quelle ville cherchez-vous un logement ?\nIl me faut dans la même phrase:\nLa ville de votre choix, votre budget minimum, maximum ou bien les deux."

                reform = self.model.create_chat_completion(messages=[
                    {"role": "system", "content": "Tu es un assistant immobilier. Réponds UNIQUEMENT en français, simplement et naturellement."},
                    {"role": "user", "content": message}
                ])

                final_response = reform["choices"][0]["message"]["content"]

                self.contexts[channel_id].append({"role": "assistant", "content": final_response})
                self.context(channel_id)

                return {
                    "type": "logement",
                    "city": None,
                    "hotels": [],
                    "text": final_response
                    }
        
            if not no_budget and data["price_min"] is None and data["price_max"] is None:
                message = "Vous avez un budget minimum ou maximum ?\nIl me faut dans la même phrase:\nLa ville de votre choix, votre budget minimum, maximum ou bien les deux."

                self.add_message(channel_id, "assistant", message)

                return {
                    "type": "logement",
                    "city": data["city"],
                    "hotels": [],
                    "text": message
                }

            if no_budget:
                data["price_min"] = None
                data["price_max"] = None


            city = data["city"]
            price_min = data["price_min"]
            price_max = data["price_max"]

            results = Houssing(city, "hotel", price_min, price_max).search()
            if not results:
                message = f"Aucun logement trouvé à {city} avec les critères spécifiés."
                self.add_message(channel_id, "assistant", message)
                return {
                    "type": "logement",
                    "city": city,
                    "hotels": [],
                    "text": message
                }

            hotel_lines = "\n".join([
                f"- {h['titre']} : {h['prix']}€\nLien: {h['url']}"
                for h in results
            ])

            if price_min is not None and price_max is not None:
                budget_info = f"entre {price_min}€ et {price_max}€"
            elif price_max is not None:
                budget_info = f"moins de {price_max}€"
            elif price_min is not None:
                budget_info = f"à partir de {price_min}€"
            else:
                budget_info = "sans budget défini"

            reform = self.model.create_chat_completion(messages=[
                    {
                        "role": "system",
                        "content": (
                            "Tu es un assistant immobilier.\n"
                            "Réponds uniquement en français.\n"
                            "Fais une réponse très courte.\n"
                            "Une seule ligne par hôtel.\n"
                            "Nom + prix + lien uniquement.\n"
                            "Aucune phrase inutile."
                        )
                    },
                {
                    "role": "user",
                    "content": f"Voici des hôtels à {city} {budget_info} :\n{hotel_lines}\n."
                }
            ],
            max_tokens=512)

            final_response = reform["choices"][0]["message"]["content"]
            self.contexts[channel_id].append({"role": "assistant", "content": final_response})
            self.context(channel_id)


            result = {"type": "logement", "city": city, "hotels": results, "text": final_response}
            if channel_id not in self.last_result:
                self.last_result[channel_id] = {}
            self.last_result[channel_id]["logement"] = result

            return result
        
        # No weather/transport/houssing asked by user
        result = self.model.create_chat_completion(
            messages=self.contexts[channel_id],
            max_tokens=300
        )
        response = result["choices"][0]["message"]["content"]
        response += "\n\n*N'oublions pas que je suis tout de même un assistant spécialisé dans le voyage (météo, trains, hôtels).*"
        self.contexts[channel_id].append({"role": "assistant", "content": response})
        self.context(channel_id)
        return { "type": "other", "text": response }