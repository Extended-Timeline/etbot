import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='&')

# ET Server IDs
# senator = '<@&691576535781605417>'
# global senatorial_voting  # 698212804808671294
# global senate  # 694963794757156952
# global staff_bot_commands  # 498634929064771605
# yes_vote = '<:Yes:698226023795261451>'
# no_vote = '<:No:698226052899799130>'
# abstain_vote = '<:Abstain:698226077113516118>'


# Testing IDs
senator = '<@&867863600973742121>'
global senatorial_voting  # 867857838142783529
global senate  # 867738868181368855
global staff_bot_commands  # 885604958609756190
yes_vote = '<:Yes:867869297329176587>'
no_vote = '<:No:867869349041799198>'
abstain_vote = '<:Abstain:867869367601070081>'
recycle = '♻️'
ear_with_hearing_aid = '🦻'
global channels


@bot.event
async def on_ready():
    # setting global variables on launch
    global channels
    channels = {
        "senate": bot.get_channel(694963794757156952),
        "senatorial_voting": bot.get_channel(698212804808671294),
        "staff_bot_commands": bot.get_channel(498634929064771605),
        "memes": bot.get_channel(888136237146337280)
    }
    global senatorial_voting
    senatorial_voting = bot.get_channel(867857838142783529)
    global senate
    senate = bot.get_channel(867738868181368855)
    global staff_bot_commands
    staff_bot_commands = bot.get_channel(885604958609756190)

    print('Anwesend {}'.format(bot.user.name))


# checks if the author is *not* the bot himself
def is_not_me(m):
    return not m.author == bot.user


# returns the index of the last bill
async def get_last_billnumber():  # TODO use something else (database?) to store the current index
    history = await senatorial_voting.history().flatten()
    message = discord.utils.find(lambda m: m.content.startswith('**Bill '), history)
    return to_int(message.content.split(' ')[1])


# cleans first x characters (command)
def remove_command(message, amount):
    result = ''
    for i, c in enumerate(message):
        if i > amount:
            result += c
    return result


def assemble_bill(text, number: int, author):
    text = '**Bill ' + str(number) + ':** ' + '\r\n' + text + ' '
    text += '\r\n' + 'Bill by: ' + author + ' '
    text += '\r\n' + senator
    return text


def assemble_amendment(message, index, billnumber, author):
    message = '**Bill ' + str(index) + ':** Amendment to **Bill ' + str(billnumber) + '** ' + '\r\n' + str(message)
    message += '\r\n' + 'Bill by: ' + str(author) + ' '
    message += '\r\n' + str(senator)
    return message


# checks if string is digit
def is_number(string):
    string = str(string)
    if not string:
        return False
    for char in string:
        if char not in '0123456789':
            return False
    return True


# remove leading digits (all digits until a character is not a number)
def clean_digits(text):
    check = False
    cleantext = ''
    for char in text:
        if not is_number(char) or check is True:
            if check:
                cleantext += char
            check = True
    return cleantext


# removes everything but numbers from a string and converts it to an integer
def to_int(string):
    number = ''
    for c in string:
        if is_number(c):
            number += c

    if number == '':
        return None
    return int(number)


# takes the whole command/message as input and assembles and sends the bill
@bot.command(name='bill')
async def make_bill(context, *, text):  # TODO strip the leading space in text
    # delete the command
    await context.message.delete()

    # make bill
    number = await get_last_billnumber() + 1
    text = assemble_bill(text, number, context.author.mention)

    # send bill
    message = await senatorial_voting.send(text)

    # add reactions
    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(abstain_vote)


# takes the whole command/message as input and assembles and sends the amendment
@bot.command(name='amendment',
             aliases=['amend'])
async def make_amendment(context, billnumber: to_int, *, text):
    # delete the command
    await context.message.delete()

    if not is_number(billnumber):
        return

    # assemble new message
    number = await get_last_billnumber() + 1
    text = assemble_amendment(text, number, billnumber, context.author.mention)

    # errors
    if billnumber >= number:
        await senate.send('You can\'t amend a non-existent bill.' + context.author.mention)
        return

    # send command
    message = await senatorial_voting.send(text)

    # add reactions
    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(abstain_vote)


@bot.command(name='edit',
             aliases=['editbill', 'editamendment'])
async def edit(context, index: to_int, *, text):
    # delete the command
    await context.message.delete()

    number = await get_last_billnumber() + 1

    # errors
    if index >= number:
        await context.author.send('You can\'t amend a non-existent bill.')
        return

    if not is_number(index):
        await context.author.send(index + ' is not a valid number.')
        return

    history = await senatorial_voting.history().flatten()
    original = discord.utils.find(lambda m: m.content.startswith('**Bill ' + str(index)), history)

    tmp = original.content.split(' ')
    if not tmp[len(tmp) - 2] == context.author.mention:
        await context.author.send('You cannot edit a bill that is not yours.')
        return

    changes = original.content.split(' ')

    if original == '':
        await context.author.send('No bill with that number was found.')
        return

    # clean changes
    changes = changes[:len(changes) - 4]
    changestemp = ''
    for element in changes:
        changestemp = changestemp + element + ' '
    changes = changestemp

    if changes[2] == 'Amendment' and changes[3] == 'to':
        billnumber = to_int(changes[5])
        content = assemble_amendment(text, index, billnumber, context.author.mention)
    else:
        content = assemble_bill(text, index, context.author.mention)

    # edit command
    await original.edit(content=content)
    await senate.send(
        'Previous wording: ' + '\r\n' + '```' + changes + '```' + '\r\n' + 'Success. ' + context.author.mention)


@bot.command(name='option',
             aliases=['options', 'optionbill', 'optionsbill'])
async def make_option(context, amount: to_int, *, text):
    # deletes command message
    await context.message.delete()

    # variable set up
    number = await get_last_billnumber() + 1

    # assemble new bill
    text = assemble_bill(text, number, context.author.mention)

    # send option
    await send_option(text, senatorial_voting, amount)


@bot.command(name='amendmentoption',
             aliases=['amendmentoptions', 'optionamendment', 'optionsamendment'])
async def make_amendmentoption(context, billnumber: to_int, amount: to_int, *, text):
    # deletes command message
    await context.message.delete()

    number = await get_last_billnumber() + 1

    # errors
    if billnumber >= number:
        await context.author.send('You can\'t amend a non-existent bill.')
        return

    if not is_number(billnumber):
        await context.author.send(billnumber + ' is not a valid number.')
        return

    if not is_number(amount):
        await context.author.send(amount + ' is not a valid number.')
        return

    # assemble new amendment
    text = assemble_amendment(text, number, billnumber, context.author.mention)

    # send option
    await send_option(text, senatorial_voting, amount)


async def send_option(text, channel, amount):
    # send amendment
    text = await channel.send(text)

    # add reactions
    if amount < 2:
        await text.add_reaction('1️⃣')
        await text.add_reaction('2️⃣')
    elif amount == 3:
        await text.add_reaction('1️⃣')
        await text.add_reaction('2️⃣')
        await text.add_reaction('3️⃣')
    elif amount == 4:
        await text.add_reaction('1️⃣')
        await text.add_reaction('2️⃣')
        await text.add_reaction('3️⃣')
        await text.add_reaction('4️⃣')
    elif amount == 5:
        await text.add_reaction('1️⃣')
        await text.add_reaction('2️⃣')
        await text.add_reaction('3️⃣')
        await text.add_reaction('4️⃣')
        await text.add_reaction('5️⃣')
    elif amount > 5:
        await text.add_reaction('1️⃣')
        await text.add_reaction('2️⃣')
        await text.add_reaction('3️⃣')
        await text.add_reaction('4️⃣')
        await text.add_reaction('5️⃣')
        await text.add_reaction('6️⃣')

    await text.add_reaction(no_vote)
    await text.add_reaction(abstain_vote)


async def meme_voting(message):
    if len(message.embeds) < 1:
        return

    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(recycle)
    await message.add_reaction(ear_with_hearing_aid)


@bot.event
async def on_message(message):
    # no reaction if bot
    if message.author.bot:
        return

    # this is so commands continue to work
    await bot.process_commands(message)

    # meme voting
    if message.channel == channels["memes"]:
        await meme_voting(message)


bot.run('Nzc3ODY3NDAxNTQyMTA3MTQ4.X7JreA.RhAvIT0kp-BAB30SsduZh1wipT8')
