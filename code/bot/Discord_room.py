import discord
import asyncio


"""
Discord private rooms

This file allows creation, deletion, and cancellation of private rooms
using buttons.

It provides:
- Creation of a private room per user
- Access restriction (only the creator of the room can view and write in it)
- Deletion button with a cancellation option

Components:

1. CreateTextRoomView

- Checks if the room already exists
- Creates a new private room
- Sends a confirmation message in the interaction response
- Sends a message with a link to the private room if the room already exists
- Creates a button to close the room in the private room

2. DeleteTextRoom

- Checks if the room exists
- Checks if the click comes from the right user
- Sends a message in the channel to warn the user about closing the private room
- Creates a button to allow the user to cancel the deletion

3. CancelDeleteView

- Starts a background asyncio task that waits before deleting the private room
- Allows the user to cancel, which stops the deletion task
- If cancelled, the channel stays active
"""

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
            return

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
    
        await asyncio.sleep(2)
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
