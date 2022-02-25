from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from disnake.ext.commands import ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionFailed, NoEntryPointError, \
    ExtensionNotLoaded


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Admin(bot))
    print("Loaded Admin Cog.")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="cogs",
                            description="Replies with a list of all the loaded cogs.")
    @commands.has_guild_permissions(administrator=True)
    async def cogs(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        cogs: str = str(list(self.bot.cogs.keys()))
        await inter.edit_original_message(content=cogs)

    @commands.slash_command(name="load",
                            description="Loads a cog.")
    @commands.has_guild_permissions(administrator=True)
    async def load(self, inter: ApplicationCommandInteraction, cog: str):
        await inter.response.defer()
        try:
            self.bot.load_extension(cog)
        except (ExtensionNotFound, ExtensionAlreadyLoaded, NoEntryPointError, ExtensionFailed) as e:
            await inter.edit_original_message(content=e)
            return
        await inter.edit_original_message(content="Cog loaded.")

    @commands.slash_command(name="unload",
                            description="Unloads a cog.")
    @commands.has_guild_permissions(administrator=True)
    async def unload(self, inter: ApplicationCommandInteraction, cog: str):
        await inter.response.defer()
        try:
            self.bot.unload_extension(cog)
        except (ExtensionNotFound, ExtensionNotLoaded) as e:
            await inter.edit_original_message(content=e)
            return
        await inter.edit_original_message(content="Cog unloaded.")

    @commands.slash_command(name="reload",
                            description="RelLoads a cog.")
    @commands.has_guild_permissions(administrator=True)
    async def reload(self, inter: ApplicationCommandInteraction, cog: str):
        await inter.response.defer()
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except (ExtensionNotFound, ExtensionNotLoaded, ExtensionAlreadyLoaded, NoEntryPointError, ExtensionFailed) as e:
            await inter.edit_original_message(content=e)
            return
        await inter.edit_original_message(content="Cog reloaded.")
