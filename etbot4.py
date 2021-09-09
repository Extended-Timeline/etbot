import discord

client = discord.Client()


@client.event
async def on_ready():
    print('Anwesend {}'.format(client.user.name))


def is_not_me(m):
    return not m.author == client.user


def get_index():  # increase index by 1 + save
    text = open('index.txt', 'r')
    nummer = text.read()
    text.close()
    nummer = int(nummer) + 1
    return nummer


def increase_index():
    text = open('index.txt', 'r')
    number = int(text.read())
    text.close()
    text = open('index.txt', 'w')
    text.write(str(number + 1))
    text.close()


def remove_command(message, amount):  # cleans first x letters (command)
    messagenew = ''
    for x in range(len(message)):
        if x > amount:
            messagenew = messagenew + message[x]
    return messagenew


def message_start(message, nummer):
    message = '**Bill ' + str(nummer) + ':** ' + '\r\n' + message + ' '
    return message


def message_end(message, author):  # assembles the message end
    message = message + '\r\n' + 'Bill by: ' + author + ' '
    message = message + '\r\n' + senator
    return message


def is_number(string):  # checks if str is digit
    string = str(string)
    for char in string:
        if not char in '0123456789':
            return False
    return True


def clean_digits(message):
    check = False
    cleanmessage = ''
    for x in range(len(message)):
        if not is_number(message[x]) or check == True:
            if check:
                cleanmessage = cleanmessage + message[x]
            check = True
    return cleanmessage


global senator
senator = '<@&691576535781605417>'
global senatorial_voting
senatorial_voting = 698212804808671294
global senate
senate = 694963794757156952
global yes_vote
yes_vote = '<:Yes:698226023795261451>'
global no_vote
no_vote = '<:No:698226052899799130>'
global abstain_vote
abstain_vote = '<:Abstain:698226077113516118>'
global staff_bot_commands
staff_bot_commands = 498634929064771605


@client.event
async def on_message(message):
    # no reaction if bot
    if message.author.bot:
        return

    # in #senatorial-voting or in #senate and &edit
    if message.channel.id == senatorial_voting or (message.channel.id == senate and (
            message.content.startswith('&edit') or message.content.startswith(
        'Edit'))) or message.channel.id == staff_bot_commands:

        # variable set up
        message = message.content  # get message
        author = message.author.mention  # get author
        channel = client.get_channel(senate)  # channel for sending back feedback

        # bill scenario
        if message.content.startswith('&bill ') or message.content.startswith('&Bill '):
            # deletes command message
            await message.channel.purge(limit=1, check=is_not_me)

            # variable set up
            nummer = get_index()

            # assemble new message
            message = remove_command(message, 5)
            message = message_start(message, nummer)
            message = message_end(message, author)

            # send message
            message = await message.channel.send(message)
            increase_index()

            # add reactions
            await message.add_reaction(yes_vote)
            await message.add_reaction(no_vote)
            await message.add_reaction(abstain_vote)

        # edit command
        if message.content.startswith('&edit ') or message.content.startswith('&Edit '):

            # variable set up
            args = message.split(' ')
            index = str(args[1])  # get index
            isamendment = False

            # clean command + digit
            message = remove_command(message, 5)
            message = clean_digits(message)

            # search bill by index
            channelhistory = client.get_channel(senatorial_voting)  # replace
            messages = await channelhistory.history(limit=40).flatten()
            y = -1
            for x in range(len(messages)):
                message2 = messages[x].content.split(' ')
                if len(message2) > 1:
                    message1 = message2[1]
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
                    'Either no bill with that index in the last 40 messages or other invalid input.' + author)
                return
            if not authorbill == author:
                await message.channel.send('This is not your Bill. ' + author)
                return

            # assamble new message
            if isamendment:
                message = '**Bill ' + str(index) + ':** Amendment to **Bill ' + str(
                    billnumber) + '** ' + '\r\n' + message + ' '
            else:
                message = message_start(message, index)
            message = message_end(message, author)

            # edit message
            await messages[y].edit(content=message)
            await channel.send(
                'Original wording: ' + '\r\n' + '```' + changes + '```' + '\r\n' + 'Success. ' + author)

        # option scenario
        if message.content.startswith('&option ') or message.content.startswith('&Option '):

            # deletes command message
            await message.channel.purge(limit=1, check=is_not_me)

            # variable set up
            args = message.split(' ')
            amount = args[1]  # get number
            if not is_number(amount):
                return
            amount = int(amount)
            nummer = get_index()

            # assemble new message
            message = remove_command(message, 7)
            message = clean_digits(message)
            message = message_start(message, nummer)
            message = message_end(message, author)

            # send message
            message = await message.channel.send(message)
            increase_index()

            # add reactions
            if amount < 2:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
            elif amount == 3:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
            elif amount == 4:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
            elif amount == 5:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
                await message.add_reaction('5️⃣')
            elif amount > 5:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
                await message.add_reaction('5️⃣')
                await message.add_reaction('6️⃣')

            await message.add_reaction(no_vote)
            await message.add_reaction(abstain_vote)

        # amendment scenario
        if message.content.startswith('&amendment ') or message.content.startswith('&Amendment '):

            # deletes command message
            await message.channel.purge(limit=1, check=is_not_me)

            # variable set up
            args = message.split(' ')
            billnumber = args[1]  # get bill number
            if not is_number(billnumber):
                print(billnumber, '1')
                return
            billnumber = int(billnumber)
            nummer = get_index()

            # assemble new message
            message = remove_command(message, 10)
            message = clean_digits(message)
            message = '**Bill ' + str(nummer) + ':** Amendment to **Bill ' + str(
                billnumber) + '** ' + '\r\n' + message + ' '
            message = message_end(message, author)

            # errors
            text = open('index.txt', 'r')
            check = int(text.read())
            text.close()
            if check < billnumber:
                channel = client.get_channel(senate)
                await channel.send('''You can't amend a non-existant bill.''' + author)
                return

            # send message
            message = await message.channel.send(message)
            increase_index()

            # add reactions
            await message.add_reaction(yes_vote)
            await message.add_reaction(no_vote)
            await message.add_reaction(abstain_vote)

        # amendment option
        if message.content.startswith('&amendmentoption ') or message.content.startswith('&Amendmentoption '):

            # deletes command message
            await message.channel.purge(limit=1, check=is_not_me)

            # variable set up
            args = message.split(' ')
            billnumber = args[1]  # get bill number
            if not is_number(billnumber):
                return
            billnumber = int(billnumber)
            amount = args[2]  # get options amount
            if not is_number(amount):
                return
            amount = int(amount)
            nummer = get_index()

            # assemble new message
            message = remove_command(message, 16)
            message = clean_digits(message)
            message = clean_digits(message)
            message = '**Bill ' + str(nummer) + ':** Amendment to **Bill ' + str(
                billnumber) + '** ' + '\r\n' + message + ' '
            message = message_end(message, author)

            # errors
            text = open('index.txt', 'r')
            check = int(text.read())
            text.close()
            if check < billnumber:
                channel = client.get_channel(senate)
                await channel.send('''You can't amend a non-existant bill.''' + author)
                return

            # send message
            message = await message.channel.send(message)
            increase_index()

            # add reactions
            if amount < 2:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
            elif amount == 3:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
            elif amount == 4:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
            elif amount == 5:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
                await message.add_reaction('5️⃣')
            elif amount > 5:
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
                await message.add_reaction('5️⃣')
                await message.add_reaction('6️⃣')

            await message.add_reaction(no_vote)
            await message.add_reaction(abstain_vote)

        # edit bill numbers
        if message.content.startswith('&index ') or message.content.startswith('&Index '):

            # variable set up
            args = message.split(' ')
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


client.run('')
