
import discord
import os
import asyncio

from llama_cpp import Llama
from dotenv import load_dotenv

from Discord_room import DeleteTextRoom, CreateTextRoomView
from LLM_asking import LLM_LLaMa_Local
from state import channel_data

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL", 0))
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
SerpAPI = os.getenv("SerpAPI")

os.environ["HF_HUB_TOKEN"] = HUGGING_FACE_TOKEN

llm = Llama.from_pretrained(
    repo_id="LiteLLMs/Mistral-7B-Instruct-v0.3-GGUF",
    filename="Q5_1/Q5_1-00001-of-00001.gguf",
    verbose=False
)

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)
print("lancement du bot")

@client.event
async def on_ready():
    print(f'Connecté : {client.user}')

    client.add_view(DeleteTextRoom())
    client.add_view(CreateTextRoomView())

    try:
        channel = await client.fetch_channel(DISCORD_CHANNEL)
    except Exception as e:
        print(f"Erreur: {e}")
        return

    async for msg in channel.history(limit=50):
        if msg.author == client.user and msg.components:
            await msg.delete()

    await channel.send(
        "Clique pour créer ton salon privé",
        view=CreateTextRoomView()
    )

used_llm = LLM_LLaMa_Local(llm, SerpAPI)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == f"salon-{message.author.id}":

        if message.channel.id not in channel_data:
            channel_data[message.channel.id] = {
                "type": None,
                "city": None
            }

        response = await asyncio.to_thread(
            used_llm.get_llm_response,
            message.content,
            message.channel.id
        )  

        if isinstance(response, dict):
            msg = response.get("message", "")
            view = response.get("view")

            if not msg or not msg.strip():
                msg = "Je n'ai pas compris 🤔"

            await message.channel.send(msg, view=view)

        else:
            if not response or not response.strip():
                response = "Je n'ai pas compris 🤔"

            await message.channel.send(response)

client.run(DISCORD_TOKEN)