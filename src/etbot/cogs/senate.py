from disnake import Message
from disnake.ext import commands

from etbot.vars import channels, roles, emojis, index


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Senate(bot))
    print("Loaded Senate Cog.")


def assemble_bill(text: str, bill_index: int, author: str) -> str:
    text = f"**Bill {str(bill_index)}:** \r\n{text}" \
           f"\r\nBill by: {author}" \
           f"\r\n{roles.senator}"
    return text


def assemble_amendment(text: str, bill_index: int, bill_number: int, author: str):
    text = f"**Bill {str(bill_index)}:** Amendment to **Bill {str(bill_number)}** " \
           f"\r\n{str(text)}" \
           f"\r\nBill by: {str(author)}" \
           f"\r\n{roles.senator}"
    return text


class Senate(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="bill", aliases=["Bill"])
    @commands.has_role("Senator")
    async def bill(self, ctx: commands.Context, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        index.increment_index()
        text: str = assemble_bill(text, index.get_index(), author)

        # send bill
        msg: Message = await channels.senatorial_voting.send(text)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="amendment", aliases=["Amendment"])
    @commands.has_role("Senator")
    async def amendment(self, ctx: commands.Context, bill_number: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            msg: Message = await ctx.message.channel.send(f"No valid bill number was given. {author}")
            await msg.delete(delay=60)

        index.increment_index()
        text: str = assemble_amendment(text, index.get_index(), bill_number, author)

        # send amendment
        msg: Message = await channels.senatorial_voting.send(text)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="option", aliases=["Option"])
    @commands.has_role("Senator")
    async def option(self, ctx: commands.Context, options: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        index.increment_index()
        text: str = assemble_bill(text, index.get_index(), author)

        msg: Message = await channels.senatorial_voting.send(text)

        # add reactions
        for i in range(0, options):
            await msg.add_reaction(emojis.options[i])
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="amendmentoption", aliases=["Amendmentoption"])
    @commands.has_role("Senator")
    async def amendment_option(self, ctx: commands.Context, bill_number: int, option_amount: int, *, text: str):
        pass

    @commands.command(name="edit", aliases=["Edit"])
    @commands.has_role("Senator")
    async def edit(self, ctx: commands.Context, bill_number: int, *, text: str):
        pass

    @commands.command(name="index", aliases=["Index"])
    @commands.has_guild_permissions(administrator=True)
    async def set_index(self, ctx: commands.Context, new_index: int):
        index.set_index(new_index)
        msg: Message = await ctx.channel.send(f"Index set to {new_index}.")
        await msg.delete(delay=60)
