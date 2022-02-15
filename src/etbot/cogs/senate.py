from disnake import Message
from disnake.ext import commands

from vars import channels, roles, emojis, index

_history_limit: int = 500


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Senate(bot))
    print("Loaded Senate Cog.")


async def check_bill_closed(bill: Message) -> bool:
    for reaction in bill.reactions:
        if reaction.emoji in [emojis.bill_closed, emojis.imperial_authority, emojis.void, emojis.withdrawn]:
            return True
    return False


async def find_bill(bot: commands.Bot, bill_number: int) -> Message | None:
    messages = await channels.get_senatorial_voting().history(limit=_history_limit).flatten()

    for msg in messages:  # TODO make this work better and not depend on precise spacing...
        content: list[str] = msg.content.split(' ')
        if len(content) <= 1:
            continue
        if to_int(content[1]) == bill_number and msg.author == bot.user:
            return msg
    return None


def assemble_bill(text: str, bill_index: int, author: str) -> str:
    text = f"**Bill {str(bill_index)}:** " \
           f"\r\n{text} " \
           f"\r\nBill by: {author} " \
           f"\r\n{roles.senator}"
    return text


def assemble_amendment(text: str, bill_index: int, bill_number: int, author: str) -> str:
    text = f"**Bill {str(bill_index)}:** Amendment to **Bill {str(bill_number)}** " \
           f"\r\n{str(text)} " \
           f"\r\nBill by: {str(author)} " \
           f"\r\n{roles.senator}"
    return text


def senatorial_channels_check(ctx: commands.Context) -> bool:
    # Add special channel permissions for specific commands by making a special case for it
    allowed_channels: list[channels]
    match ctx.command.qualified_name:
        case "edit":
            allowed_channels = [channels.get_senate()]
        case "index":
            allowed_channels = [channels.get_staff_bot_commands()]
        case _:
            allowed_channels = [channels.get_senate(),
                                channels.get_senatorial_voting(),
                                channels.get_staff_bot_commands()]
    return ctx.message.channel in allowed_channels


# removes everything but numbers from a string and converts it to an integer
def to_int(string: str) -> int | None:
    number = ''
    for c in string:
        if c.isdigit():
            number += c

    if number == '':
        return None
    return int(number)


class Senate(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="bill", aliases=["Bill"],
                      brief="Assembles a bill with the given text.",
                      help="Usage: &bill [bill_text] \n"
                           "Assembles a bill with the given text. \n"
                           "Including mentioning senators and adding the reactions in the correct order.")
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
        msg: Message = await channels.get_senatorial_voting().send(text)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="amendment", aliases=["Amendment"],
                      brief="Assembles an amendment with the given text and bill_number.",
                      help="Usage: &amendment [bill_number] [amendment_text] \n"
                           "Assembles an amendment with the given text and bill_number. \n"
                           "Including mentioning senators and adding the reactions in the correct order.")
    @commands.has_role("Senator")
    @commands.check(senatorial_channels_check)
    async def amendment(self, ctx: commands.Context, bill_number: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            await channels.get_senate().send(f"No valid bill number was given. {author}"
                                             f"\r\n```{ctx.message.clean_content}```")
            return

        index.increment_index()
        text: str = assemble_amendment(text, index.get_index(), bill_number, author)

        # send amendment
        msg: Message = await channels.get_senatorial_voting().send(text)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="option", aliases=["Option"],
                      brief="Assembles an option bill with the given text.",
                      help="Usage: &option [option_number] [amendment_text] \n"
                           "Assembles a bill with the given text and amount of options. \n"
                           "Including mentioning senators and adding the reactions in the correct order.")
    @commands.has_role("Senator")
    @commands.check(senatorial_channels_check)
    async def option(self, ctx: commands.Context, options: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        index.increment_index()
        text: str = assemble_bill(text, index.get_index(), author)

        msg: Message = await channels.get_senatorial_voting().send(text)

        # add reactions
        for i in range(0, options):
            await msg.add_reaction(emojis.options[i])
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="amendmentoption", aliases=["Amendmentoption"],
                      brief="Assembles an option amendment with the given text and bill.",
                      help="Usage: &amendmentoption [bill_number] [option_number 2-6] [amendment_text] \n"
                           "Assembles an amendment with the given text and bill_number and amount of options. \n"
                           "Including mentioning senators and adding the reactions in the correct order.")
    @commands.has_role("Senator")
    @commands.check(senatorial_channels_check)
    async def amendment_option(self, ctx: commands.Context, bill_number: int, options: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            await ctx.message.channel.send(f"No valid bill number was given. {author}"
                                           f"\r\n```{ctx.message.clean_content}```")
            return

        index.increment_index()
        text: str = assemble_amendment(text, index.get_index(), bill_number, author)

        msg: Message = await channels.get_senatorial_voting().send(text)

        # add reactions
        for i in range(0, options):
            await msg.add_reaction(emojis.options[i])
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

    @commands.command(name="edit", aliases=["Edit"],
                      brief="Edits the bill with the given number.",
                      help="Usage: &edit [bill_number] [new_text] \n"
                           "Edits the bill with the given number. \n"
                           "Will return an error if you are not the original author of the bill to be edited.")
    @commands.has_role("Senator")
    @commands.check(senatorial_channels_check)
    async def edit(self, ctx: commands.Context, bill_index: int, *, text: str):
        # deletes bill command
        await ctx.message.delete()

        # variable set up
        author: str = ctx.author.mention

        # check that bill_number is valid
        if bill_index > index.get_index():
            await ctx.message.channel.send(f"No valid bill number was given. {author}"
                                           f"\r\n```{ctx.message.clean_content}```")
            return

        is_amendment = False

        # search bill by index TODO check if bill has been concluded before editing
        original: Message | None = await find_bill(self.bot, bill_index)
        # error message
        if original is None:
            await ctx.channel.send(f"No bill with that index in the last {_history_limit} messages. {author}"
                                   f"\r\n```{ctx.message.clean_content}```")
            return
        # check that the bill isn't closed already
        if await check_bill_closed(original):
            await ctx.channel.send(f"You cannot edit an already closed bill. {author}"
                                   f"\r\n```{ctx.message.clean_content}```")
            return

        content: list[str] | None = original.content.split(' ')
        bill_author: str | None = content[len(content) - 2]
        bill_number: str | None = None
        if content[2] == 'Amendment' and content[3] == 'to':
            bill_number = content[5]
            bill_number = bill_number.strip('*')
            is_amendment = True

        # clean changes
        changes = content[:len(content) - 4]
        changes_string: str = ''
        for element in changes:
            changes_string += f"{element} "

        # error message
        if not author == bill_author:
            await ctx.channel.send(f"This is not your Bill. {author}"
                                   f"\r\n```{ctx.message.clean_content}```")
            return

        # assemble new message
        if is_amendment:
            content_string: str = assemble_amendment(text, bill_index, int(bill_number), author)
        else:
            content_string: str = assemble_bill(text, bill_index, author)

        # edit command
        if original is not None:
            await original.edit(content=content_string)
            await channels.get_senate().send(f"Previous wording: "
                                             f"\r\n```{changes_string}```"
                                             f"\r\nSuccess. {author}")
        else:
            await channels.get_senate().send("A bug seems to have crept itself into the code.")

    @commands.command(name="index", aliases=["Index"],
                      brief="Overrides the saved bill index.",
                      help="Usage: &index [new_index] \n"
                           "Overrides the saved bill index. \n"
                           "Only to be used in case of an error with the automatic counting.")
    @commands.has_guild_permissions(administrator=True)
    @commands.check(senatorial_channels_check)
    async def set_index(self, ctx: commands.Context, new_index: int):
        index.set_index(new_index)
        msg: Message = await ctx.channel.send(f"Index set to {new_index}.")
        await msg.delete(delay=60)
