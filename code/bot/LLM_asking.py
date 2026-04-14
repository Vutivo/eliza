import json

from Weather import weather

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
                        '{"output":"weather","city":"CITY","days":N} or {"output":"other"}'
                    )
                },
                # Examples
                {"role": "user", "content": "météo à Paris ?"},
                {"role": "assistant", "content": '{"output":"weather","city":"Paris","days":0}'},
                {"role": "user", "content": "température à Lyon demain"},
                {"role": "assistant", "content": '{"output":"weather","city":"Lyon","days":1}'},
                {"role": "user", "content": "il fait chaud à Nantes dans 2 jours ?"},
                {"role": "assistant", "content": '{"output":"weather","city":"Nantes","days":2}'},
                {"role": "user", "content": "raconte moi une blague"},
                {"role": "assistant", "content": '{"output":"other"}'},
                {"role": "user", "content": "c'est quoi la capitale de l'Espagne ?"},
                {"role": "assistant", "content": '{"output":"other"}'},
                # Real message we asking for:
                {"role": "user", "content": message}
            ],
            max_tokens=50 # limit to have shot JSON
        )
        response = result["choices"][0]["message"]["content"].strip()
        print("JSON Format:", response)
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
            print(f"[WEATHER] city={city}, days={days}")

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

        # No weather asked by user
        result = self.model.create_chat_completion(
            messages=self.contexts[channel_id],
            max_tokens=300
        )
        response = result["choices"][0]["message"]["content"]
        self.contexts[channel_id].append({"role": "assistant", "content": response})
        self.context(channel_id)

        return response
