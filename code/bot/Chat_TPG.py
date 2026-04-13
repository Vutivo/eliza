import discord
import os
import asyncio # allow making timers
import requests
import json
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv


"""All private key from .env"""
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL", 0))
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

"""LLM Mistral"""
os.environ["HF_HUB_TOKEN"] = HUGGING_FACE_TOKEN # Necessary to validate token by hugging face

llm = Llama.from_pretrained(
	repo_id="LiteLLMs/Mistral-7B-Instruct-v0.3-GGUF",
	filename="Q5_1/Q5_1-00001-of-00001.gguf",
    verbose=False # desactivate messages from terminal
)

intents = discord.Intents.all() # all permissions
intents.message_content = True

client = discord.Client(intents=intents)
print("lancement du bot")

class LLM_LLaMa_Local:
    def __init__(self, model):
        self.model = model
        self.contexts = {}

    def get_llm_response(self, user_message, channel_id):
        if channel_id not in self.contexts: # to store for new channel

            prompt = [{
                "role":"system",
                "content": (
                    "Tu es un assistant avec des outils. "
                    "Si on te demande le temps qu'il fait, repond SEULEMENT en JSON : "
                    '{"tools":"weather", "city":"Nantes", "days":1}.'
                    "Sinon répond normalement et demande si l'utilisateur a besoin de quelque chose."
                )
            }]
            self.contexts[channel_id] = prompt

        self.contexts[channel_id].append({ # clean storage of user message
            "role" : "user",
            "content" : user_message
        })

        mistral = self.model.create_chat_completion( # add response for next interaction
            messages=self.contexts[channel_id],
            max_tokens=120
        )

        response = mistral["choices"][0]["message"]["content"]

        try:
            data = json.loads(response)
            if "tools" in data:
                if data["tools"]=="weather":
                    city = data["city"]
                    days = data["days"] # ??? days = data.get("days", 0)

                    results_weather = WeatherPerDate(city, days)

                reform = self.model.create_chat_completion(
                    {
                    "role": "system",
                    "content": "Transforme les données en phrase"
                    },
                    {
                    "role": "user",
                    "content": str(weather)
                    }
                )
                final_response = mistral["choices"][0]["message"]["content"]
                self.contexts[channel_id].append({
                    "role" : "assistant",
                    "content" : response
                })
                return final_response
        except:
            pass
        
        self.contexts[channel_id].append({
            "role": "assistant",
            "content": response
        })

        if len(self.contexts[channel_id]) > 20: # store only 20 last messages
            self.contexts[channel_id] = self.contexts[prompt] + self.contexts[channel_id][-20:]

        return response

class CreateTextRoomView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # make the button permanent

    @discord.ui.button(label="Créer mon salon privé", custom_id="create_channel")
    async def create_text_room(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user

        write_perm = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), # No one can see the channel
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True) # Allow only the user who clicked so see and write in the channel
        }
        for channel in guild.text_channels:
            if channel.name == f"salon-{member.id}":
                await interaction.response.send_message(
                    f"Vous avez déjà un salon privé.\nPour ouvrir une nouvelle session vous devez clore la précédante !\nVotre salon : {channel.mention}",
                    ephemeral=True,
                    delete_after=5 # delete message after 5s
                    )
                
                return
            
        channel = await guild.create_text_channel(
            name=f"salon-{member.id}",
            overwrites=write_perm
        )

        await interaction.response.send_message(
            f"Ton salon privé a été créé",
            ephemeral=True,
            delete_after=10
        )

        await channel.send(
            "Clique pour clore la discution",
            view=DeleteTextRoom()
        )

class DeleteTextRoom(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Clore le salon privé", custom_id="delete_channel")
    async def close_private_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            private_channel_user = int(interaction.channel.name.split("-")[1])
        except:
            await interaction.response.send_message("Le salon n'existe pas")
            return
        
        if interaction.user.id != private_channel_user:
            await interaction.response.send_message("Non autorisé", delete_after=3)

        channel = interaction.channel
        await interaction.response.send_message(
            "Fermeture du salon dans 10 secondes",
            delete_after=10)
        await channel.send(view=CancelDeleteView(channel))

class CancelDeleteView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel_to_delete = channel
        self.task = asyncio.create_task(self._delete_after_delay())

    async def _delete_after_delay(self):
    
        await asyncio.sleep(10)
        try:
            await self.channel_to_delete.delete()
        except:
            print("Problème au niveau de la suppression")
            pass
        
    @discord.ui.button(label="Annuler la fermeture", custom_id="cancel_delete")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.task.cancel()
        await interaction.response.send_message(
            "Suppression du salon annulée !",
            delete_after=3
        )
        await interaction.message.delete()

class WeatherPerDate(discord.ui.View):
    async def weather(self, interaction: discord.Interaction, city: str, days: int=0):
    
        if days == 0:
            url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
            
            res = requests.get(url)
            data = res.json()
            temp_c = data['current']['temp_c']
            return (f"A {city}: {temp_c}°C")
        else:
            url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days={days}&aqi=no&alerts=no"
            
            res = requests.get(url)
            data = res.json()

            if "error" in data:
                return "Aucune ville avec ce nom n'a été trouvé"
            else:
                forecast_day_min_temp = data['forecast']['forecastday'][0]['day']['mintemp_c']
                forecast_day_max_temp = data['forecast']['forecastday'][0]['day']['maxtemp_c']

                return(f"A {city}: Minimum température : {forecast_day_min_temp}, Maximum température : {forecast_day_max_temp}")

@client.event
async def on_ready():
    print(f'Connecté : {client.user}')

    client.add_view(DeleteTextRoom())  # Make persistant button
    client.add_view(CreateTextRoomView())

    try:
        channel = await client.fetch_channel(DISCORD_CHANNEL)  # try to catch channel
    except Exception as e:
        print(f"Erreur: {e}")


    async for msg in channel.history(limit=50):
        if msg.author == client.user and msg.components:
            await msg.delete()

    await channel.send(
        "Clique pour créer ton salon privé",
        view=CreateTextRoomView()
    )

used_llm = LLM_LLaMa_Local(llm) # use pretrained llm here

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == f"salon-{message.author.id}":

        response = used_llm.get_llm_response(
            message.content,
            message.channel.id
        )

        await message.channel.send(response)

client.run(DISCORD_TOKEN)


# prendre les mots clés dans le prompt de l'utilisateur pour les utiliser en fonction