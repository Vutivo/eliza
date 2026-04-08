import discord
import os
import asyncio # pour faire des timers
from dotenv import load_dotenv
load_dotenv()


intents = discord.Intents.all() # toutes les permissions
intents.message_content = True

client = discord.Client(intents=intents)
print("lancement du bot")


class CreateTextRoomView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Il sera toujours la

    @discord.ui.button(label="Créer mon salon privé", custom_id="create_channel")
    async def create_text_room(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user

        write_perm = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), # Personne ne vois le channel
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True) # Donne l'autorisation de voir et écrire seulement à celui qui a cliquer
        }
        for channel in guild.text_channels:
            if channel.name == f"salon-{member.id}":
                await interaction.response.send_message(
                    f"Vous avez déjà un salon privé.\nPour ouvrir une nouvelle session vous devez clore la précédante !\nVotre salon : {channel.mention}",
                    ephemeral=True,
                    delete_after=5 # supprime le message après 5s

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


@client.event
async def on_ready():
    print(f'Connecté : {client.user}')

    client.add_view(DeleteTextRoom()) # Pour ne pas recrée un message si il est déjà mis
    client.add_view(CreateTextRoomView()) # Pour ne pas recrée un message si il est déjà mis

    channel_id = int(os.getenv("DISCORD_CHANNEL"))
    channel = client.get_channel(channel_id)

    async for msg in channel.history(limit=50): # On enleve les doublons
        if msg.author == client.user and msg.components:
            await msg.delete()

    await channel.send(
        "Clique pour créer ton salon privé",
        view=CreateTextRoomView()
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('hello'):
        await message.channel.send('Hello!')

client.run(os.getenv("DISCORD_TOKEN"))

# ajout d'un bouton pour annuler dans la fonction delete entre le asynctio et le delete pour return et ne pas delete