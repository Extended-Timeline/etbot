from urllib import request

from disnake.ext import commands
from disnake.ext.commands import ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionFailed, NoEntryPointError, \
    ExtensionNotLoaded


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Admin(bot))
    print("Loaded Admin Cog.")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="cogs", aliases=["Cogs"],
                      brief="Replies with a list of all the loaded cogs.")
    @commands.has_guild_permissions(administrator=True)
    async def cogs(self, ctx: commands.Context):
        cogs: str = str(list(self.bot.cogs.keys()))
        await ctx.send(cogs)

    @commands.command(name="load", aliases=["Load"],
                      brief="Loads a cog.")
    @commands.has_guild_permissions(administrator=True)
    async def load(self, ctx: commands.Context, cog: str):
        try:
            self.bot.load_extension(cog)
        except (ExtensionNotFound, ExtensionAlreadyLoaded, NoEntryPointError, ExtensionFailed) as e:
            await ctx.send(e)
            return
        await ctx.send("Cog loaded.")

    @commands.command(name="unload", aliases=["Unload"],
                      brief="Unloads a cog.")
    @commands.has_guild_permissions(administrator=True)
    async def unload(self, ctx: commands.Context, cog: str):
        try:
            self.bot.unload_extension(cog)
        except (ExtensionNotFound, ExtensionNotLoaded) as e:
            await ctx.send(e)
            return
        await ctx.send("Cog unloaded.")

    @commands.command(name="reload", aliases=["Reload"],
                      brief="RelLoads a cog.")
    @commands.has_guild_permissions(administrator=True)
    async def reload(self, ctx: commands.Context, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except (ExtensionNotFound, ExtensionNotLoaded, ExtensionAlreadyLoaded, NoEntryPointError, ExtensionFailed) as e:
            await ctx.send(e)
            return
        await ctx.send("Cog reloaded.")

    @commands.command(name="ip", aliases=["IP"],
                      brief="Replies with the server's IP.")
    @commands.has_guild_permissions(administrator=True)
    async def ip(self, ctx: commands.Context):
        ipv4: str
        ipv6: str
        ipv4 = request.urlopen('https://v4.ident.me').read().decode('utf8')
        if ipv4 != "":
            await ctx.reply(ipv4)
            return
        ipv6 = request.urlopen('https://v6.ident.me').read().decode('utf8')
        if ipv6 != "":
            await ctx.reply(ipv6)
            return
        await ctx.reply("Could not get IP.")
