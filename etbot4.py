import discord

client = discord.Client()

# ET Server IDs
# senator = '<@&691576535781605417>'
# senatorial_voting = client.get_channel(698212804808671294)
# senate = client.get_channel(694963794757156952)
# staff_bot_commands = client.get_channel(498634929064771605)
# yes_vote = '<:Yes:698226023795261451>'
# no_vote = '<:No:698226052899799130>'
# abstain_vote = '<:Abstain:698226077113516118>'

# Testing IDs
senator = '<@&867863600973742121>'
senatorial_voting = client.get_channel(867857838142783529)  # is now the channel itself, not it's ID.
senate = client.get_channel(867738868181368855)  # to get the ID just use senate.id
staff_bot_commands = client.get_channel(885604958609756190)
yes_vote = '<:Yes:867869297329176587>'
no_vote = '<:No:867869349041799198>'
abstain_vote = '<:Abstain:867869367601070081>'


@client.event
async def on_ready():
    print('Anwesend {}'.format(client.user.name))


def is_not_me(m):
    return not m.author == client.user


# increase index by 1 + save
def get_index():
    text = open('index.txt', 'r')
    number = text.read()
    text.close()
    number = int(number) + 1
    return number


# increase index by 1
def increase_index():
    file = open('index.txt', 'r')
    index = int(file.read())
    file.close()
    file = open('index.txt', 'w')
    file.write(str(index + 1))
    file.close()


# cleans first x characters (command)
def remove_command(nachricht, amount):
    nachrichtnew = ''
    for x in range(len(nachricht)):
        if x > amount:
            nachrichtnew = nachrichtnew + nachricht[x]
    return nachrichtnew


def bill_start(nachricht, nummer):
    nachricht = '**Bill ' + str(nummer) + ':** ' + '\r\n' + nachricht + ' '
    return nachricht


# assembles the command end
def message_end(nachricht, author):
    nachricht = nachricht + '\r\n' + 'Bill by: ' + author + ' '
    nachricht = nachricht + '\r\n' + senator
    return nachricht


# checks if str is digit
def is_number(string):
    string = str(string)
    for char in string:
        if char not in '0123456789':
            return False
    return True


# remove leading digits (all digits until no more
def clean_digits(nachricht):
    check = False
    cleantext = ''
    for char in nachricht:
        if not is_number(char) or check is True:
            if check:
                cleantext = cleantext + char
            check = True
    return cleantext


# takes the whole command/message as input and assembles and sends the bill
async def make_bill(command):
    # variable set up
    nachricht = command.content  # get command
    author = command.author.mention  # get author

    # deletes bill command
    await command.channel.purge(limit=1, check=is_not_me)

    # assemble new bill
    nachricht = remove_command(nachricht, 5)
    nachricht = bill_start(nachricht, get_index())
    nachricht = message_end(nachricht, author)

    # send bill
    message = await senatorial_voting.send(nachricht)
    increase_index()

    # add reactions
    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(abstain_vote)


# takes the whole command/message as input and assembles and sends the amendment
async def make_amendment(command):
    # variable set up
    nachricht = command.content  # get command
    author = command.author.mention  # get author

    # deletes command command
    await command.channel.purge(limit=1, check=is_not_me)

    # variable set up
    args = nachricht.split(' ')
    billnumber = args[1]  # get command number
    if not is_number(billnumber):
        print(billnumber, '1')
        return
    billnumber = int(billnumber)
    number = get_index()

    # assemble new message
    nachricht = remove_command(nachricht, 10)
    nachricht = clean_digits(nachricht)
    nachricht = '**Bill ' + str(number) + ':** Amendment to **Bill ' + str(
        billnumber) + '** ' + '\r\n' + nachricht + ' '
    nachricht = message_end(nachricht, author)

    # errors
    text = open('index.txt', 'r')
    check = int(text.read())
    text.close()
    if check < billnumber:
        await senate.send('You can\'t amend a non-existent bill.' + author)
        return

    # send command
    nachricht = await senatorial_voting.send(nachricht)
    increase_index()

    # add reactions
    await nachricht.add_reaction(yes_vote)
    await nachricht.add_reaction(no_vote)
    await nachricht.add_reaction(abstain_vote)


async def send_option(nachricht, channel, amount):
    # send amendment
    nachricht = await channel.send(nachricht)
    increase_index()

    # add reactions
    if amount < 2:
        await nachricht.add_reaction('1️⃣')
        await nachricht.add_reaction('2️⃣')
    elif amount == 3:
        await nachricht.add_reaction('1️⃣')
        await nachricht.add_reaction('2️⃣')
        await nachricht.add_reaction('3️⃣')
    elif amount == 4:
        await nachricht.add_reaction('1️⃣')
        await nachricht.add_reaction('2️⃣')
        await nachricht.add_reaction('3️⃣')
        await nachricht.add_reaction('4️⃣')
    elif amount == 5:
        await nachricht.add_reaction('1️⃣')
        await nachricht.add_reaction('2️⃣')
        await nachricht.add_reaction('3️⃣')
        await nachricht.add_reaction('4️⃣')
        await nachricht.add_reaction('5️⃣')
    elif amount > 5:
        await nachricht.add_reaction('1️⃣')
        await nachricht.add_reaction('2️⃣')
        await nachricht.add_reaction('3️⃣')
        await nachricht.add_reaction('4️⃣')
        await nachricht.add_reaction('5️⃣')
        await nachricht.add_reaction('6️⃣')

    await nachricht.add_reaction(no_vote)
    await nachricht.add_reaction(abstain_vote)


async def make_option(command):
    # variable set up
    nachricht = command.content  # get command
    author = command.author.mention  # get author

    # deletes command message
    await command.channel.purge(limit=1, check=is_not_me)

    # variable set up
    args = nachricht.split(' ')
    amount = args[1]  # get number
    if not is_number(amount):
        return
    amount = int(amount)
    number = get_index()

    # assemble new bill
    nachricht = remove_command(nachricht, 7)
    nachricht = clean_digits(nachricht)
    nachricht = bill_start(nachricht, number)
    nachricht = message_end(nachricht, author)

    # send option
    await send_option(nachricht, senatorial_voting, amount)


async def make_amendmentoption(command):
    # variable set up
    nachricht = command.content  # get command
    author = command.author.mention  # get author

    # deletes command command
    await command.channel.purge(limit=1, check=is_not_me)

    # variable set up
    args = nachricht.split(' ')
    billnumber = args[1]  # get command number
    if not is_number(billnumber):
        return
    billnumber = int(billnumber)
    amount = args[2]  # get options amount
    if not is_number(amount):
        return
    amount = int(amount)
    number = get_index()

    # assemble new amendment
    nachricht = remove_command(nachricht, 16)
    nachricht = clean_digits(nachricht)
    nachricht = '**Bill ' + str(number) + ':** Amendment to **Bill ' + str(
        billnumber) + '** ' + '\r\n' + nachricht + ' '
    nachricht = message_end(nachricht, author)

    # errors
    text = open('index.txt', 'r')
    check = int(text.read())
    text.close()
    if check < billnumber:
        await senate.send('You can\'t amend a non-existent bill.' + author)
        return

    # send option
    await send_option(nachricht, senatorial_voting, amount)


async def set_index(command):
    # variable set up
    nachricht = command.content  # get command
    author = command.author.mention  # get author

    # variable set up
    args = nachricht.split(' ')
    indexnew = args[1]  # get newindex
    if not is_number(indexnew):
        await senate.send('That\'s not a number. ' + author)
        return

    # edit index
    text = open('index.txt', 'w')
    text.write(str(int(indexnew) - 1))
    text.close()

    # response
    await senate.send('Success, the next bill number will be: ' + indexnew + '. ' + author)


@client.event
async def on_message(message):
    # no reaction if bot
    if message.author.bot:
        return

    # in #senatorial-voting or in #senate and &edit
    if (message.channel.id == senatorial_voting.id or (
            message.channel == senate and (message.content.startswith('&edit') or
                                           message.content.startswith('&Edit'))) or
            message.channel == staff_bot_commands):

        # variable set up
        nachricht = message.content  # get bill
        author = message.author.mention  # get author

        # bill scenario
        if message.content.startswith('&bill ') or message.content.startswith('&Bill '):
            await make_bill(message)

        # edit bill
        if message.content.startswith('&edit ') or message.content.startswith('&Edit '):

            # variable set up
            args = nachricht.split(' ')
            index = str(args[1])  # get index
            isamendment = False

            # clean command + digit
            nachricht = remove_command(nachricht, 5)
            nachricht = clean_digits(nachricht)

            # search bill by index
            channelhistory = client.get_channel(senatorial_voting.id)  # replace
            messages = await channelhistory.history(limit=40).flatten()
            y = -1
            for x in range(len(messages)):
                message2 = messages[x].content.split(' ')
                if len(message2) > 1:
                    message1 = message2[1]  # TODO make to_number() function
                    message1 = message1.strip('*')
                    message1 = message1.strip(':')
                    if str(message1) == index and messages[x].author == client.user:
                        y = x
                        if message2[2] == 'Amendment' and message2[3] == 'to':
                            billnumber = message2[5]
                            billnumber = billnumber.strip('*')
                            isamendment = True
                        changes = message2
                        authorbill = message2[len(message2) - 2]

            # clean changes
            changes = changes[:len(changes) - 4]
            changestemp = ''
            for element in changes:
                changestemp = changestemp + element + ' '
            changes = changestemp

            # error messages
            if y == -1:
                await message.channel.send(
                    'Either no command with that index in the last 40 messages or other invalid input.' + author)
                return
            if not author == authorbill:
                await message.channel.send('This is not your Bill. ' + author)
                return

            # assamble new command
            if isamendment:
                nachricht = '**Bill ' + str(index) + ':** Amendment to **Bill ' + str(
                    billnumber) + '** ' + '\r\n' + nachricht + ' '
            else:
                nachricht = bill_start(nachricht, index)
            nachricht = message_end(nachricht, author)

            # edit command
            await messages[y].edit(content=nachricht)
            await senate.send(
                'Original wording: ' + '\r\n' + '```' + changes + '```' + '\r\n' + 'Success. ' + author)

        # option scenario
        if message.content.startswith('&option ') or message.content.startswith('&Option '):
            await make_option(message)

        # amendment scenario
        if message.content.startswith('&amendment ') or message.content.startswith('&Amendment '):
            await make_amendment(message)

        # amendment option
        if message.content.startswith('&amendmentoption ') or message.content.startswith('&Amendmentoption '):
            await make_amendmentoption(message)

        # edit command numbers
        if message.content.startswith('&index ') or message.content.startswith('&Index '):
            await set_index(message)


client.run('Nzc3ODY3NDAxNTQyMTA3MTQ4.X7JreA.RhAvIT0kp-BAB30SsduZh1wipT8')
