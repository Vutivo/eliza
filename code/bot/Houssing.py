import discord

class Houssing(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Appartement", style=discord.ButtonStyle.primary)
    async def appartement(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Voici les appartements que j'ai trouvé pour vous !"
        )

    @discord.ui.button(label="Maison", style=discord.ButtonStyle.success)
    async def maison(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Voici les maisons disponibles !"
        )

    @discord.ui.button(label="Je ne sais pas", style=discord.ButtonStyle.secondary)
    async def inconnu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Pas de souci, je vais t'aider à choisir 😉"
        )