from disnake import Message
from disnake.ext import commands

from vars import messages


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Support(bot))
    print("Loaded Support Cog.")


class Support(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="support", aliases=["Support"])
    async def support(self, ctx: commands.Context):
        msg: Message = await messages.get_support()
        await ctx.channel.send(msg.content)
