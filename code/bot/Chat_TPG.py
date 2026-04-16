import discord
import os
import asyncio # allow making timer

from llama_cpp import Llama
from dotenv import load_dotenv
# From our files
from Discord_room import DeleteTextRoom, CreateTextRoomView
from LLM_asking import LLM_LLaMa_Local
from discord.ext import commands

"""
Discord Bot with Local LLM (Mistral 7B)

This script initializes and runs a Discord bot with a local LLM.
The bot allows users to create private text channels and interact with
an AI travel assistant inside these private channels.

Features:
- Private channel creation when clicking a button
- Delete channel when clicking a delete button in the private channel
- Cancel channel deletion when clicking a cancel button in the private channel
- All buttons are persistent to ensure they still work when the bot restarts
- Local LLM from HuggingFace
- Asynchronous processing for smooth LLM responses

Example:
1. User clicks the creation button -> private room created
2. User sends a message -> LLM generates a response -> replies in the same channel
3. User clicks the deletion button -> cancel button appears
4.1. User does not click -> room is deleted
4.2. User clicks the cancel button -> room stays open
"""

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL", 0))
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

os.environ["HF_HUB_TOKEN"] = HUGGING_FACE_TOKEN # Necessary to validate token by hugging face

llm = Llama.from_pretrained(
	repo_id="LiteLLMs/Mistral-7B-Instruct-v0.3-GGUF",
	filename="Q5_1/Q5_1-00001-of-00001.gguf",
    verbose=False # desactivate messages from terminal
)

intents = discord.Intents.all() # all permissions
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
print("lancement du bot")


@client.event
async def on_ready():
    print(f'Connecté : {client.user}')

    await client.tree.sync()

    client.add_view(DeleteTextRoom())  # Make persistant button
    client.add_view(CreateTextRoomView())

    try:
        channel = await client.fetch_channel(DISCORD_CHANNEL)  # try to catch channel
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

used_llm = LLM_LLaMa_Local(llm) # use pretrained llm here

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == f"salon-{message.author.id}":

        async with message.channel.typing():
            response = await asyncio.to_thread(
                used_llm.get_llm_response,
                message.content,
                message.channel.id
            )
        await message.channel.send(response["text"])

@client.tree.command(name="recap", description="Récapitulatif des dernières recherches")
async def recap(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    all_last = used_llm.last_result.get(channel_id, {})

    if not all_last:
        await interaction.response.send_message("Aucune recherche effectuée.", delete_after=3)
        return

    embeds = []

    if "weather" in all_last:
        last = all_last["weather"]
        embed = discord.Embed(title=f"🌤️ Météo — {last['city']}", description=last.get("text"), color=0x5bc0eb)
        embeds.append(embed)

    if "train" in all_last:
        last = all_last["train"]
        embed = discord.Embed(title=f"🚆 Trains — {last['from']} → {last['to']}", description=last.get("text"), color=0x2ecc71)
        embeds.append(embed)

    if "logement" in all_last:
        last = all_last["logement"]
        embed = discord.Embed(title=f"🏨 Hôtels — {last['city']}", color=0xe67e22)
        for h in last.get("hotels", []):
            embed.add_field(name=f"{h['titre']} — {h['prix']}€", value=h['url'], inline=False)
        embeds.append(embed)

    for embed in embeds:
        embed.set_footer(text="Assistant voyage")

    if embeds:
        await interaction.response.send_message(embeds=embeds)
    else:
        await interaction.response.send_message("Aucune recherche connue.", delete_after=3)
        
client.run(DISCORD_TOKEN)