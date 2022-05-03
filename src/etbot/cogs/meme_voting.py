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

        meme_channels = [channels.get_memes(), channels.get_religious_memes()]
        # meme voting
        if message.channel in meme_channels:
            await vote_on_meme(message)

    @commands.command(name="meme", aliases=["Meme"],
                      brief="Adds the meme voting reactions to the referenced message.",
                      help="Adds the meme voting reactions to the referenced message.")
    async def meme(self, ctx: commands.Context):
        # deletes meme command
        await ctx.message.delete()

        # variable set up
        msg: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        # add reactions
        await vote_on_meme(msg)

    @commands.command(name="vote", aliases=["Vote"],
                      brief="Assembles a vote with the given text.",
                      help="Assembles a vote with the given text. \n"
                           "Including adding the reactions in the correct order.")
    async def vote(self, ctx: commands.Context):
        # deletes vote command
        await ctx.message.delete()

        # variable set up
        msg: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)
