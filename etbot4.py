import discord

client = discord.Client()


@client.event
async def on_ready():
    print('Anwesend {}'.format(client.user.name))


def is_not_me(m):
    return not m.author == client.user


def get_index():  # increase index by 1 + save
    text = open('index.txt', 'r')
    number = text.read()
    text.close()
    number = int(number) + 1
    return number


def increase_index():
    file = open('index.txt', 'r')
    index = int(file.read())
    file.close()
    file = open('index.txt', 'w')
    file.write(str(index + 1))
    file.close()


def remove_command(nachricht, amount):  # cleans first x characters (command)
    nachrichtnew = ''
    for x in range(len(nachricht)):
        if x > amount:
            nachrichtnew = nachrichtnew + nachricht[x]
    return nachrichtnew


def bill_start(nachricht, nummer):
    nachricht = '**Bill ' + str(nummer) + ':** ' + '\r\n' + nachricht + ' '
    return nachricht


def message_end(nachricht, author):  # assembles the command end
    nachricht = nachricht + '\r\n' + 'Bill by: ' + author + ' '
    nachricht = nachricht + '\r\n' + senator
    return nachricht


def is_number(string):  # checks if str is digit
    string = str(string)
    for char in string:
        if char not in '0123456789':
            return False
    return True


def clean_digits(nachricht):  # remove leading digits (all digits until no more
    check = False
    cleantext = ''
    for char in nachricht:
        if not is_number(char) or check is True:
            if check:
                cleantext = cleantext + char
            check = True
    return cleantext


# ET Server IDs
# senator = '<@&691576535781605417>'
# senatorial_voting = 698212804808671294
# senate = 694963794757156952
# yes_vote = '<:Yes:698226023795261451>'
# no_vote = '<:No:698226052899799130>'
# abstain_vote = '<:Abstain:698226077113516118>'
# staff_bot_commands = 498634929064771605

# Testing IDs
senator = '<@&867863600973742121>'
senatorial_voting = 867857838142783529
senate = 867738868181368855
yes_vote = '<:Yes:867869297329176587>'
no_vote = '<:No:867869349041799198>'
abstain_vote = '<:Abstain:867869367601070081>'
staff_bot_commands = 885604958609756190


async def make_bill(command):
    # variable set up
    nachricht = command.content  # get command
    author = command.author.mention  # get author
    channel = client.get_channel(senate)  # channel for sending back feedback

    # deletes bill command
    await command.channel.purge(limit=1, check=is_not_me)

    # assemble new bill
    nachricht = remove_command(nachricht, 5)
    nachricht = bill_start(nachricht, get_index())
    nachricht = message_end(nachricht, author)

    # send bill
    message = await command.channel.send(nachricht)
    increase_index()

    # add reactions
    await message.add_reaction(yes_vote)
    await message.add_reaction(no_vote)
    await message.add_reaction(abstain_vote)


async def set_index(message):
    # variable set up
    author = message.author.mention
    args = message.content.split(' ')
    indexnew = args[1]  # get newindex
    if not is_number(indexnew):
        await message.channel.send('That\'s not a number. ' + author)
        return

    # edit index
    text = open('index.txt', 'w')
    text.write(str(int(indexnew) - 1))
    text.close()

    # response
    await message.channel.send('Success, the next bill number will be: ' + indexnew + '. ' + author)


@client.event
async def on_message(message):
    # no reaction if bot
    if message.author.bot:
        return

    # in #senatorial-voting or in #senate and &edit
    if (message.channel.id == senatorial_voting or (
            message.channel.id == senate and (message.content.startswith('&edit') or
                                              message.content.startswith('&Edit'))) or
            message.channel.id == staff_bot_commands):

        # variable set up
        nachricht = message.content  # get bill
        author = message.author.mention  # get author
        channel = client.get_channel(senate)  # channel for sending back feedback

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
            channelhistory = client.get_channel(senatorial_voting)  # replace
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
                        print(authorbill)

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
            await channel.send(
                'Original wording: ' + '\r\n' + '```' + changes + '```' + '\r\n' + 'Success. ' + author)

        # option scenario
        if message.content.startswith('&option ') or message.content.startswith('&Option '):

            # deletes command command
            await message.channel.purge(limit=1, check=is_not_me)

            # variable set up
            args = nachricht.split(' ')
            amount = args[1]  # get number
            if not is_number(amount):
                return
            amount = int(amount)
            number = get_index()

            # assemble new command
            nachricht = remove_command(nachricht, 7)
            nachricht = clean_digits(nachricht)
            nachricht = bill_start(nachricht, number)
            nachricht = message_end(nachricht, author)

            # send command
            nachricht = await message.channel.send(nachricht)
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

        # amendment scenario
        if message.content.startswith('&amendment ') or message.content.startswith('&Amendment '):

            # deletes command command
            await message.channel.purge(limit=1, check=is_not_me)

            # variable set up
            args = nachricht.split(' ')
            billnumber = args[1]  # get command number
            if not is_number(billnumber):
                print(billnumber, '1')
                return
            billnumber = int(billnumber)
            number = get_index()

            # assemble new command
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
                channel = client.get_channel(senate)
                await channel.send('''You can't amend a non-existant command.''' + author)
                return

            # send command
            nachricht = await message.channel.send(nachricht)
            increase_index()

            # add reactions
            await nachricht.add_reaction(yes_vote)
            await nachricht.add_reaction(no_vote)
            await nachricht.add_reaction(abstain_vote)

        # amendment option
        if message.content.startswith('&amendmentoption ') or message.content.startswith('&Amendmentoption '):

            # deletes command command
            await message.channel.purge(limit=1, check=is_not_me)

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

            # assemble new command
            nachricht = remove_command(nachricht, 16)
            nachricht = clean_digits(nachricht)
            nachricht = clean_digits(nachricht)
            nachricht = '**Bill ' + str(number) + ':** Amendment to **Bill ' + str(
                billnumber) + '** ' + '\r\n' + nachricht + ' '
            nachricht = message_end(nachricht, author)

            # errors
            text = open('index.txt', 'r')
            check = int(text.read())
            text.close()
            if check < billnumber:
                channel = client.get_channel(senate)
                await channel.send('''You can't amend a non-existant command.''' + author)
                return

            # send command
            nachricht = await message.channel.send(nachricht)
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

        # edit command numbers
        if message.content.startswith('&index ') or message.content.startswith('&Index '):
            await set_index(message)


client.run('Nzc3ODY3NDAxNTQyMTA3MTQ4.X7JreA.RhAvIT0kp-BAB30SsduZh1wipT8')
