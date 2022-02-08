from disnake import Message
from disnake.ext import commands

from src.etbot.vars import channels, roles, emojis, index


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Senate(bot))
    print("Loaded Senate Cog.")


def assemble_bill(text: str, bill_index: int, author: str) -> str:
    text = f"**Bill {str(bill_index)}:** " \
           f"\r\n{text} " \
           f"\r\nBill by: {author} " \
           f"\r\n{roles.senator}"
    return text


def assemble_amendment(text: str, bill_index: int, bill_number: int, author: str):
    text = f"**Bill {str(bill_index)}:** Amendment to **Bill {str(bill_number)}** " \
           f"\r\n{str(text)} " \
           f"\r\nBill by: {str(author)} " \
           f"\r\n{roles.senator}"
    return text


def senatorial_channels_check(ctx: commands.Context) -> bool:
    # Add special channel permissions for specific commands by making a special case for it
    match ctx.command.qualified_name:
        case "edit":
            allowed_channels: list[channels] = [channels.senate]
        case _:
            allowed_channels: list[channels] = [channels.senate,
                                                channels.senatorial_voting,
                                                channels.staff_bot_commands]
    return ctx.message.channel in allowed_channels


# removes everything but numbers from a string and converts it to an integer
def to_int(string: str):
    number = ''
    for c in string:
        if c.isdigit():
            number += c

    if number == '':
        return number
    return int(number)


class Senate(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="bill", aliases=["Bill"])
    @commands.has_role("Senator")
    @commands.check(senatorial_channels_check)
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
    @commands.check(senatorial_channels_check)
    async def amendment(self, ctx: commands.Context, bill_number: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            msg: Message = await ctx.message.channel.send(f"No valid bill number was given. {author}")
            await msg.delete(delay=60)
            return

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
    @commands.check(senatorial_channels_check)
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
    @commands.check(senatorial_channels_check)
    async def amendment_option(self, ctx: commands.Context, bill_number: int, options: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            msg: Message = await ctx.message.channel.send(f"No valid bill number was given. {author}")
            await msg.delete(delay=60)
            return

        index.increment_index()
        text: str = assemble_amendment(text, index.get_index(), bill_number, author)

        msg: Message = await channels.senatorial_voting.send(text)

        # add reactions
        for i in range(0, options):
            await msg.add_reaction(emojis.options[i])
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="edit", aliases=["Edit"])
    @commands.has_role("Senator")
    @commands.check(senatorial_channels_check)
    async def edit(self, ctx: commands.Context, bill_index: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_index > index.get_index():
            msg: Message = await ctx.message.channel.send(f"No valid bill number was given. {author}")
            await msg.delete(delay=60)
            return

        is_amendment = False

        # search bill by index TODO check if bill has been concluded before editing
        messages = await channels.senatorial_voting.history(limit=40).flatten()
        original: Message | None = None
        changes: list[str] | None = None
        bill_author: str | None = None
        bill_number: str | None = None

        for msg in messages:  # TODO make this work better and not depend on precise spacing...
            content: list[str] = msg.content.split(' ')
            if len(content) <= 1:
                continue
            if to_int(content[1]) == bill_index and msg.author == self.bot.user:
                original = msg
                changes = content
                bill_author = content[len(content) - 2]
                if content[2] == 'Amendment' and content[3] == 'to':
                    bill_number = content[5]
                    bill_number = bill_number.strip('*')
                    is_amendment = True
                break

        # clean changes
        changes = changes[:len(changes) - 4]
        changes_string: str | None = None
        for element in changes:
            changes_string = f"{changes_string}{element} "

        # error messages
        if original is None:
            msg: Message = await ctx.channel.send(f"No bill with that index in the last 40 messages. {author}")
            await msg.delete(delay=60)
            return
        if not author == bill_author:
            msg: Message = await ctx.channel.send(f"This is not your Bill. {author}")
            await msg.delete(delay=60)
            return

        # assemble new message
        if is_amendment:
            content_string: str = assemble_amendment(text, bill_index, int(bill_number), author)
        else:
            content_string: str = assemble_bill(text, bill_index, author)

        # edit command
        if original is not None:
            await original.edit(content=content_string)
            await channels.senate.send(
                f"Previous wording: \r\n```{changes_string}```\r\nSuccess. {author}")
        else:
            await channels.senate.send("A bug seems to have crept itself into the code.")

    @commands.command(name="index", aliases=["Index"])
    @commands.has_guild_permissions(administrator=True)
    @commands.check(senatorial_channels_check)
    async def set_index(self, ctx: commands.Context, new_index: int):
        index.set_index(new_index)
        msg: Message = await ctx.channel.send(f"Index set to {new_index}.")
        await msg.delete(delay=60)
