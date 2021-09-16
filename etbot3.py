import discord

client = discord.Client()

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
global commands


@client.event
async def on_ready():
    # setting global variables on launch
    global channels
    channels = {
        "senate": client.get_channel(694963794757156952),
        "senatorial_voting": client.get_channel(698212804808671294),
        "staff_bot_commands": client.get_channel(498634929064771605),
        "memes": client.get_channel(888136237146337280)
    }
    global commands
    commands = {
        "&bill": [channels["senatorial_voting"],
                  channels["staff_bot_commands"]],

        "&amendment": [channels["senatorial_voting"],
                       channels["staff_bot_commands"]],

        "&edit": [channels["senate"],
                  channels["senatorial_voting"],
                  channels["staff_bot_commands"]],

        "&option": [channels["senatorial_voting"],
                    channels["staff_bot_commands"]],

        "&amendmentoption": [channels["senatorial_voting"],
                             channels["staff_bot_commands"]],

        "&index": [channels["staff_bot_commands"]]
    }
    global senatorial_voting
    senatorial_voting = client.get_channel(867857838142783529)
    global senate
    senate = client.get_channel(867738868181368855)
    global staff_bot_commands
    staff_bot_commands = client.get_channel(885604958609756190)

    print('Anwesend {}'.format(client.user.name))


# checks if the author is *not* the bot himself
def is_not_me(m):
    return not m.author == client.user


# returns the index
def get_index():
    text = open('index.txt', 'r')
    number = text.read()
    text.close()
    number = int(number) + 1
    return number


# increases index by 1
def increase_index():
    file = open('index.txt', 'r')
    index = int(file.read())
    file.close()
    file = open('index.txt', 'w')
    file.write(str(index + 1))
    file.close()


# cleans first x characters (command)
def remove_command(message, amount):
    result = ''
    for i, c in enumerate(message):
        if i > amount:
            result += c
    return result


def assemble_bill(message, number, author):
    message = '**Bill ' + str(number) + ':** ' + '\r\n' + message + ' '
    message += '\r\n' + 'Bill by: ' + author + ' '
    message += '\r\n' + senator
    return message


def assemble_amendment(message, index, billnumber, author):
    message = '**Bill ' + str(index) + ':** Amendment to **Bill ' + str(billnumber) + '** ' + '\r\n' + str(message)
    message += '\r\n' + 'Bill by: ' + str(author) + ' '
    message += '\r\n' + str(senator)
    return message


# checks if string is digit
def is_number(string):
    string = str(string)
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
        return number
    return int(number)


# takes the whole command/message as input and assembles and sends the bill
async def make_bill(command):
    # variable set up
    text = command.content  # get command
    author = command.author.mention  # get author

    # deletes bill command
    await command.channel.purge(limit=1, check=is_not_me)

    # assemble new bill
    text = remove_command(text, 5)
    text = assemble_bill(text, get_index(), author)

    # send bill
    message = await senatorial_voting.send(text)
    increase_index()

    # add reactions
    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(abstain_vote)


# takes the whole command/message as input and assembles and sends the amendment
async def make_amendment(command):
    # deletes command command
    await command.channel.purge(limit=1, check=is_not_me)

    # variable set up
    text = command.content  # get command
    author = command.author.mention  # get author

    args = text.split(' ')

    billnumber = to_int(args[1])  # get index
    if billnumber == '':
        await command.channel.send('No valid bill number was given ' + author)
        return

    if not is_number(billnumber):
        print(billnumber, '1')
        return
    billnumber = int(billnumber)
    number = get_index()

    # assemble new message
    text = remove_command(text, 10)
    text = clean_digits(text)
    text = assemble_amendment(text, number, billnumber, author)

    # errors
    file = open('index.txt', 'r')
    index = int(file.read())
    file.close()
    if index < billnumber:
        await senate.send('You can\'t amend a non-existent bill.' + author)
        return

    # send command
    message = await senatorial_voting.send(text)
    increase_index()

    # add reactions
    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(abstain_vote)


async def edit(command):
    # variable set up
    text = command.content
    author = command.author.mention

    args = text.split(' ')  # TODO fix two spaces resulting in empty strings
    index = to_int(args[1])  # get index
    if index == '':
        await command.channel.send('No valid bill number was given' + author)
        return
    isamendment = False

    # clean command + digit
    text = remove_command(text, 5)
    text = clean_digits(text)

    # search bill by index TODO check if bill has been concluded before editing
    messages = await senatorial_voting.history(limit=40).flatten()
    original = changes = billauthor = billnumber = ''  # initialize variables
    for i, message in enumerate(messages):
        content = message.content.split(' ')
        if len(content) > 1:
            if to_int(content[1]) == index and message.author == client.user:
                original = message
                changes = content
                billauthor = content[len(content) - 2]
                if content[2] == 'Amendment' and content[3] == 'to':
                    billnumber = content[5]
                    billnumber = billnumber.strip('*')
                    isamendment = True
                break

    if original == '':
        await command.channel.send(
            'Either no bill with that index in the last 40 messages or other invalid input.' + author)
        return

    # clean changes
    changes = changes[:len(changes) - 4]
    changestemp = ''
    for element in changes:
        changestemp = changestemp + element + ' '
    changes = changestemp

    # error messages
    if not author == billauthor:
        await command.channel.send('This is not your Bill. ' + author)
        return

    # assemble new message
    if isamendment:
        content = assemble_amendment(text, index, billnumber, author)
    else:
        content = assemble_bill(text, index, author)

    # edit command
    if original != '':
        await original.edit(content=content)
        await senate.send(
            'Previous wording: ' + '\r\n' + '```' + changes + '```' + '\r\n' + 'Success. ' + author)
    else:
        await senate.send('A bug seems to have crept itself into the code.')


async def make_option(command):
    # variable set up
    text = command.content  # get bill
    author = command.author.mention  # get author

    # deletes command message
    await command.channel.purge(limit=1, check=is_not_me)

    # variable set up
    args = text.split(' ')
    amount = args[1]  # get number
    if not is_number(amount):
        return
    amount = int(amount)
    number = get_index()

    # assemble new bill
    text = remove_command(text, 7)
    text = clean_digits(text)
    text = assemble_bill(text, number, author)

    # send option
    await send_option(text, senatorial_voting, amount)


async def make_amendmentoption(command):
    # variable set up
    text = command.content  # get bill
    author = command.author.mention  # get author

    # deletes command message
    await command.channel.purge(limit=1, check=is_not_me)

    # variable set up
    args = text.split(' ')

    billnumber = to_int(args[1])  # get index
    if billnumber == '':
        await command.channel.send('No valid bill number was given' + author)
        return

    if not is_number(billnumber):
        return
    billnumber = int(billnumber)
    amount = args[2]  # get options amount
    if not is_number(amount):
        return
    amount = int(amount)
    number = get_index()

    # assemble new amendment
    text = remove_command(text, 16)
    text = clean_digits(text)
    text = assemble_amendment(text, number, billnumber, author)

    # errors
    file = open('index.txt', 'r')
    index = int(file.read())
    file.close()
    if index < billnumber:
        await senate.send('You can\'t amend a non-existent bill.' + author)
        return

    # send option
    await send_option(text, senatorial_voting, amount)


async def send_option(text, channel, amount):
    # send amendment
    text = await channel.send(text)
    increase_index()

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


async def set_index(command):
    # variable set up
    text = command.content  # get command
    author = command.author.mention  # get author

    # variable set up
    args = text.split(' ')
    indexnew = args[1]  # get newindex
    if not is_number(indexnew):
        await senate.send('That\'s not a number. ' + author)
        return

    # edit index
    file = open('index.txt', 'w')
    file.write(str(int(indexnew) - 1))
    file.close()

    # response
    await senate.send('Success, the next bill number will be: ' + indexnew + '. ' + author)


async def meme_voting(message):
    if len(message.embeds) < 1:
        return

    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(recycle)
    await message.add_reaction(ear_with_hearing_aid)


@client.event
async def on_message(message):
    # no reaction if bot
    if message.author.bot:
        return

    # in #senatorial-voting or in #senate and &edit
    if (message.channel == channels["senatorial_voting"] or (
            message.channel == channels["senate"] and message.content.lower().startswith('&edit')) or
            message.channel == channels["staff_bot_commands"]):

        # bill scenario
        if message.content.lower().startswith('&bill '):
            await make_bill(message)

        # amendment scenario
        if message.content.lower().startswith('&amendment '):
            await make_amendment(message)

        # edit bill
        if message.content.lower().startswith('&edit '):
            await edit(message)

        # option scenario
        if message.content.lower().startswith('&option '):
            await make_option(message)

        # amendment option
        if message.content.lower().startswith('&amendmentoption '):
            await make_amendmentoption(message)

        # edit command numbers
        if message.content.lower().startswith('&index '):
            await set_index(message)

    # meme voting
    if message.channel == channels["memes"]:
        await meme_voting(message)


client.run('Nzc3ODY3NDAxNTQyMTA3MTQ4.X7JreA.RhAvIT0kp-BAB30SsduZh1wipT8')
