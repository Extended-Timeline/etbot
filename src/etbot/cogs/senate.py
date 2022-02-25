from disnake import Message, ApplicationCommandInteraction
from disnake.ext import commands

from vars import channels, roles, emojis, index

_history_limit: int = 1000


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Senate(bot))
    print("Loaded Senate Cog.")


async def check_bill_concluded(bill: Message) -> bool:
    for reaction in bill.reactions:
        if reaction.emoji in [emojis.bill_closed, emojis.imperial_authority, emojis.void, emojis.withdrawn]:
            return True
    return False


def check_senatorial_channels(inter: ApplicationCommandInteraction) -> bool:
    # Add special channel permissions for specific commands by making a special case for it
    allowed_channels: list[channels]
    match inter.data.name:
        case "bill", "amendment", "option", "amendmentoption":
            allowed_channels = [channels.get_senate()]
        case "edit":
            allowed_channels = [channels.get_senate()]
        case "index":
            allowed_channels = [channels.get_staff_bot_commands()]
        case _:
            allowed_channels = [channels.get_senate(),
                                channels.get_senatorial_voting(),
                                channels.get_staff_bot_commands()]
    return inter.channel in allowed_channels


def check_is_staff(inter: ApplicationCommandInteraction) -> bool:
    return any(role in inter.author.roles for role in roles.staff_roles)


async def find_bill(bot: commands.Bot, bill_number: int) -> Message | None:
    messages = await channels.get_senatorial_voting().history(limit=_history_limit).flatten()

    for msg in messages:  # TODO make this work better and not depend on precise spacing...
        if msg.author != bot.user:
            continue
        if roles.senator not in msg.role_mentions:
            continue

        content: list[str] = msg.content.split(' ')
        if len(content) <= 1:
            continue
        if to_int(content[1]) != bill_number:
            continue
        return msg
    return None


def count_votes(bill: Message) -> str:
    yes: int = -1
    no: int = -1
    abstain: int = -1
    for reaction in bill.reactions:
        match reaction.emoji:
            case emojis.yes_vote:
                yes += reaction.count
            case emojis.no_vote:
                no += reaction.count
            case emojis.abstain_vote:
                abstain += reaction.count
    return f"\r\n{yes} {emojis.yes_vote} | {no} {emojis.no_vote} | {abstain} {emojis.abstain_vote}"


def assemble_bill(text: str, bill_index: int, author: str) -> str:
    text = f"**Bill {str(bill_index)}:** " \
           f"\r\n{text} " \
           f"\r\nBill by: {author} " \
           f"\r\n{roles.senator.mention}"
    return text


def assemble_amendment(text: str, bill_index: int, bill_number: int, author: str) -> str:
    text = f"**Bill {str(bill_index)}:** Amendment to **Bill {str(bill_number)}** " \
           f"\r\n{text} " \
           f"\r\nBill by: {author} " \
           f"\r\n{roles.senator.mention}"
    return text


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

    @commands.slash_command(name="bill",
                            description="Assembles a bill with the given text.")
    @commands.has_role("Senator")
    @commands.check(check_senatorial_channels)
    async def bill(
            self,
            inter: ApplicationCommandInteraction,
            text: str = commands.Param(
                name="bill_text",
                description="The bill's text"
            )
    ):
        await inter.response.defer(ephemeral=True)

        index.increment_index()
        text: str = assemble_bill(text, index.get_index(), inter.author.mention)

        # send bill
        msg: Message = await channels.get_senatorial_voting().send(text)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

        await inter.edit_original_message(content="Successfully posted bill.")
        await inter.delete_original_message(delay=60)

    @commands.slash_command(name="amendment",
                            description="Assembles an amendment with the given text and bill_number.")
    @commands.has_role("Senator")
    @commands.check(check_senatorial_channels)
    async def amendment(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to amend",
                gt=0
            ),
            text: str = commands.Param(
                name="amendment_text",
                description="The amendment's text"
            )
    ):
        await inter.response.defer(ephemeral=True)

        # variable set up
        author: str = inter.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            return

        index.increment_index()
        text: str = assemble_amendment(text, index.get_index(), bill_number, author)

        # send amendment
        msg: Message = await bill.reply(text)

        # add reactions
        await msg.add_reaction(emojis.yes_vote)
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

        await inter.edit_original_message(content="Successfully posted amendment.")
        await inter.delete_original_message(delay=60)

    @commands.slash_command(name="option",
                            description="Assembles an option bill with the given text.")
    @commands.has_role("Senator")
    @commands.check(check_senatorial_channels)
    async def option(
            self,
            inter: ApplicationCommandInteraction,
            options: int = commands.Param(
                name="options",
                description="The number of options in the bill",
                ge=2,
                le=6
            ),
            text: str = commands.Param(
                name="bill_text",
                description="The bill's text"
            )
    ):
        await inter.response.defer(ephemeral=True)

        index.increment_index()
        text: str = assemble_bill(text, index.get_index(), inter.author.mention)

        msg: Message = await channels.get_senatorial_voting().send(text)

        # add reactions
        for i in range(0, options):
            await msg.add_reaction(emojis.options[i])
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

        await inter.edit_original_message(content="Successfully posted option bill.")
        await inter.delete_original_message(delay=60)

    @commands.slash_command(name="amendmentoption",
                            description="Assembles an option amendment with the given text and bill.")
    @commands.has_role("Senator")
    @commands.check(check_senatorial_channels)
    async def amendment_option(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to amend",
                gt=0
            ),
            options: int = commands.Param(
                name="options",
                description="The number of options in the bill"
            ),
            text: str = commands.Param(
                name="amendment_text",
                description="The amendment's text"
            )
    ):
        await inter.response.defer(ephemeral=True)

        author: str = inter.author.mention

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            return

        index.increment_index()
        text: str = assemble_amendment(text, index.get_index(), bill_number, author)

        msg: Message = await bill.reply(text)

        # add reactions
        for i in range(0, options):
            await msg.add_reaction(emojis.options[i])
        await msg.add_reaction(emojis.no_vote)
        await msg.add_reaction(emojis.abstain_vote)

        await inter.edit_original_message(content="Successfully posted option amendment.")
        await inter.delete_original_message(delay=60)

    @commands.slash_command(name="edit",
                            description="Edits the bill with the given number.")
    @commands.has_role("Senator")
    @commands.check(check_senatorial_channels)
    async def edit(
            self,
            inter: ApplicationCommandInteraction,
            bill_index: int = commands.Param(
                name="bill_number",
                description="The number of the bill to edit",
                gt=0
            ),
            text: str = commands.Param(
                name="new_text",
                description="The bill's new text"
            )
    ):
        await inter.response.defer()

        author: str = inter.author.mention

        # check that bill_number is valid
        if bill_index > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            return

        is_amendment = False

        # search bill by index
        original: Message | None = await find_bill(self.bot, bill_index)
        # error message
        if original is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author} ")
            return
        # check that the bill isn't closed already
        if await check_bill_concluded(original):
            await inter.edit_original_message(content=f"You cannot edit an already closed bill. {author}")
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
        if inter.author.mention != bill_author:
            await inter.edit_original_message(content=f"This is not your Bill. {author}")
            return

        # assemble new message
        if is_amendment:
            content_string: str = assemble_amendment(text, bill_index, int(bill_number), author)
        else:
            content_string: str = assemble_bill(text, bill_index, author)

        # edit command
        if original is not None:
            await original.edit(content=content_string)
            await inter.edit_original_message(content=f"Previous wording: "
                                                      f"\r\n```{changes_string}```"
                                                      f"\r\nSuccess. {author}")
        else:
            await inter.edit_original_message(content="A bug seems to have crept itself into the code.")

    @commands.slash_command(name="index",
                            description="Overrides the saved bill index.")
    @commands.has_guild_permissions(administrator=True)
    @commands.check(check_senatorial_channels)
    async def set_index(
            self,
            inter: ApplicationCommandInteraction,
            new_index: int = commands.Param(
                name="new_index",
                description="The new index",
                gt=0
            )
    ):
        await inter.response.defer()
        index.set_index(new_index)
        await inter.edit_original_message(content=f"Index set to {new_index}.")

    @commands.slash_command(name="pass",
                            description="Passes the bill with the given number.")
    @commands.has_role("Emperor")
    @commands.check(check_senatorial_channels)
    async def pass_bill(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to pass",
                gt=0
            ),
            comment: str = commands.Param(
                name="comment",
                description="A comment or reason",
                default=''
            )
    ):
        await inter.response.defer(ephemeral=True)

        # variable set up
        author: str = inter.author.mention
        if comment != '':
            comment += ' '

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            await inter.delete_original_message(delay=60)
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            await inter.delete_original_message(delay=60)
            return
        # check that the bill isn't closed already
        if await check_bill_concluded(bill):
            await inter.edit_original_message(content=f"Bill has already been concluded. {author}")
            await inter.delete_original_message(delay=60)
            return

        await bill.add_reaction(emojis.bill_closed)

        content: list[str] = bill.content.split(' ')
        await bill.reply(f"Bill {bill_number} passes."
                         f"\n{comment}{content[len(content) - 2]}")

        # clean changes
        wording: str = ''
        for element in content[:len(content) - 4]:
            wording += f"{element} "

        # count votes
        wording += count_votes(bill)
        await channels.get_passed_bills().send(wording)

        await inter.delete_original_message()

    @commands.slash_command(name="fail",
                            description="Fails the bill with the given number.")
    @commands.has_role("Emperor")
    @commands.check(check_senatorial_channels)
    async def fail(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to fail",
                gt=0
            ),
            comment: str = commands.Param(
                name="comment",
                description="A comment or reason",
                default=''
            )
    ):
        await inter.response.defer()

        # variable set up
        author: str = inter.author.mention
        if comment != '':
            comment += ' '

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            await inter.delete_original_message(delay=60)
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            await inter.delete_original_message(delay=60)
            return
        # check that the bill isn't closed already
        if await check_bill_concluded(bill):
            await inter.edit_original_message(content=f"Bill has already been concluded. {author}")
            await inter.delete_original_message(delay=60)
            return

        await bill.add_reaction(emojis.bill_closed)

        content: list[str] = bill.content.split(' ')
        await bill.reply(f"Bill {bill_number} does not pass."
                         f"\n{comment}{content[len(content) - 2]}")

        await inter.delete_original_message()

    @commands.slash_command(name="veto",
                            description="Vetoes the bill with the given number.")
    @commands.has_role("Emperor")
    @commands.check(check_senatorial_channels)
    async def veto(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to fail",
                gt=0
            ),
            comment: str = commands.Param(
                name="comment",
                description="A comment or reason",
                default=''
            )
    ):
        await inter.response.defer()

        # variable set up
        author: str = inter.author.mention
        if comment != '':
            comment += ' '

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            await inter.delete_original_message(delay=60)
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            await inter.delete_original_message(delay=60)
            return
        # check that the bill isn't closed already
        if await check_bill_concluded(bill):
            await inter.edit_original_message(content=f"Bill has already been concluded. {author}")
            await inter.delete_original_message(delay=60)
            return

        await bill.add_reaction(emojis.imperial_authority)

        content: list[str] = bill.content.split(' ')
        await bill.reply(f"Bill {bill_number} is vetoed."
                         f"\r\n{comment}{content[len(content) - 2]}")

        await inter.delete_original_message()

    @commands.slash_command(name="void",
                            description="Voids the bill with the given number.")
    @commands.check(check_is_staff)
    @commands.check(check_senatorial_channels)
    async def void(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to fail",
                gt=0
            ),
            comment: str = commands.Param(
                name="comment",
                description="A comment or reason",
                default=''
            )
    ):
        await inter.response.defer(ephemerial=True)

        # variable set up
        author: str = inter.author.mention
        if comment != '':
            comment += ' '

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            await inter.delete_original_message(delay=60)
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            await inter.delete_original_message(delay=60)
            return
        # check that the bill isn't closed already
        if await check_bill_concluded(bill):
            await inter.edit_original_message(content=f"Bill has already been concluded. {author}")
            await inter.delete_original_message(delay=60)
            return

        await bill.add_reaction(emojis.void)

        content: list[str] = bill.content.split(' ')
        await bill.reply(f"Bill {bill_number} is void."
                         f"\r\n{comment}{content[len(content) - 2]}")

        await inter.delete_original_message()

    @commands.slash_command(name="withdraw",
                            description="Withdraws the bill with the given number.")
    @commands.check(check_senatorial_channels)
    async def withdraw(
            self,
            inter: ApplicationCommandInteraction,
            bill_number: int = commands.Param(
                name="bill_number",
                description="The number of the bill to fail",
                gt=0
            ),
            comment: str = commands.Param(
                name="comment",
                description="A comment or reason",
                default=''
            )
    ):
        await inter.response.defer()

        # variable set up
        author: str = inter.author.mention
        if comment != '':
            comment += ' '

        # check that bill_number is valid
        if bill_number > index.get_index():
            await inter.edit_original_message(content=f"No valid bill number was given. {author}")
            await inter.delete_original_message(delay=60)
            return

        bill = await find_bill(self.bot, bill_number)
        # error message
        if bill is None:
            await inter.edit_original_message(
                content=f"No bill with that index in the last {_history_limit} messages. {author}")
            await inter.delete_original_message(delay=60)
            return
        # check that the bill isn't closed already
        if await check_bill_concluded(bill):
            await inter.edit_original_message(content=f"Bill has already been concluded. {author}")
            await inter.delete_original_message(delay=60)
            return

        content: list[str] | None = bill.content.split(' ')
        bill_author: str | None = content[len(content) - 2]
        # error message
        if author != bill_author:
            await inter.edit_original_message(content=f"This is not your Bill. {author}")
            await inter.delete_original_message(delay=60)
            return

        await bill.add_reaction(emojis.withdrawn)

        content: list[str] = bill.content.split(' ')
        await bill.reply(f"Bill {bill_number} is withdrawn."
                         f"\r\n{comment}{content[len(content) - 2]}")

        await inter.delete_original_message()
