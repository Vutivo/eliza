import json

from Weather import weather
from Transport_by import search_trains

"""
Class LLM_LLaMa_Local to interact with local LLM

- Maintain conversation history for each channel
- Classify messages for function calling
- Call external function
- Return responses into French
"""
class LLM_LLaMa_Local:
    def __init__(self, model):
        self.model = model
        self.contexts = {}
        self.system_prompt = [{
            "role": "system",
            "content": "Tu es un assistant serviable. Réponds TOUJOURS en français, peu importe la langue de l'utilisateur."
        }]

    def context(self, channel_id):  # limit to make sure the llm will run faster
        if len(self.contexts[channel_id]) > 20:
            self.contexts[channel_id] = list(self.system_prompt) + self.contexts[channel_id][-20:]

    def classify(self, message: str):
        """Asking to LLM to classify the user writing to call functions"""
        result = self.model.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a classifier. Output ONLY raw JSON. No text, no explanation.\n"
                        '{"output":"weather","city":"CITY","days":N, "hour":H or null} or {"output":"other"}'
                    )
                },

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
            max_tokens=50 # limit to have shot JSON
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

        # looking for "weather" in the content or not
        output = self.classify(user_message)

        # if weather asked by user :
        if output.get("output") == "weather":
            city = output.get("city")
            days = int(output.get("days", 0))
            print(f"weather reconnu : city={city}, days={days}")

            results_weather = weather(city, days)

            reform = self.model.create_chat_completion(messages=[
                {"role": "system", "content": "Tu es un assistant météo. Réponds UNIQUEMENT en français en une seule phrase courte."},
                # Example
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


        # No weather/train asked by user
        result = self.model.create_chat_completion(
            messages=self.contexts[channel_id],
            max_tokens=300
        )
        response = result["choices"][0]["message"]["content"]
        self.contexts[channel_id].append({"role": "assistant", "content": response})
        self.context(channel_id)

        return response
