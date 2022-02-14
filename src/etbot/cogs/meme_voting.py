from disnake import Message
from disnake.ext import commands

from vars import channels, emojis


def setup(bot):
    bot.add_cog(MemeVoting(bot))
    print("Loaded MemeVoting Cog.")


async def vote_on_meme(message: Message):
    if len(message.embeds) < 1 and len(message.attachments) < 1:
        return

    await message.add_reaction(emojis.yes_vote)
    await message.add_reaction(emojis.no_vote)
    await message.add_reaction(emojis.recycle)
    await message.add_reaction(emojis.ear_with_hearing_aid)


class MemeVoting(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        # no reaction if bot
        if message.author.bot:
            return

        # meme voting
        if message.channel == channels.get_memes():
            await vote_on_meme(message)
