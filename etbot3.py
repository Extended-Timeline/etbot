import discord




client = discord.Client()

@client.event
async def on_ready():
    print('Anwesend {}'.format(client.user.name))

def is_not_me(m):
    return not m.author == client.user

def get_index(): #increase index by 1 + save
    text = open('index.txt', 'r')
    nummer = text.read()
    text.close
    nummer = int(nummer) + 1
    return nummer

def increase_index():
    text = open('index.txt', 'r')
    nummer = text.read()
    text.close
    text = open('index.txt', 'w')
    text.write(str(int(nummer) +1))
    text.close

def remove_command(nachricht, amount): #cleans first x letters (command)
    nachrichtnew = ''
    for x in range(len(nachricht)):
        if x > amount:
            nachrichtnew = nachrichtnew + nachricht[x]
    return nachrichtnew

def message_start(nachricht, nummer):
    nachricht = '**Bill ' + str(nummer) + ':** ' + ('\r\n') + nachricht + ' '
    return nachricht

def message_end(nachricht, author): #assembles the message end
    nachricht = nachricht + ('\r\n') + 'Bill by: ' + author + ' '
    nachricht = nachricht + ('\r\n') + senator
    return nachricht

def is_number(n): #checks if str is digit
    n = str(n)
    check = True
    for zeichen in n:
        if not zeichen in '0123456789':
            check = False
    return check

def clean_digits(nachricht):
    check = False
    nachrichtnew = ''
    for x in range(len(nachricht)):
        if not is_number(nachricht[x]) or check == True:
            if check == True:
                nachrichtnew = nachrichtnew + nachricht[x]
            check = True
    return nachrichtnew

global senator
senator = '<@&867863600973742121>'
global senatorial_voting
senatorial_voting = 867857838142783529
global senate
senate = 867738868181368855
global yes_vote
yes_vote = '<:Yes:867869297329176587>'
global no_vote
no_vote = '<:No:867869349041799198>'
global abstain_vote
abstain_vote = '<:Abstain:867869367601070081>'
global staff_bot_commands
staff_bot_commands = 885604958609756190

@client.event
async def on_message(message):

    #no reaction if bot
    if message.author.bot:
        return


    #in #senatorial-voting or in #senate and &edit
    if message.channel.id == senatorial_voting or ( message.channel.id == senate and (message.content.startswith('&edit') or message.content.startswith('Edit')) ) or message.channel.id == staff_bot_commands:
        
        #variable set up
        nachricht = message.content #get message
        author = message.author.mention #get author
        kanal = client.get_channel(senate) #channel for sending back feedback



        #bill scenario
        if message.content.startswith('&bill ') or message.content.startswith('&Bill '):
        
            #deletes command message
            await message.channel.purge(limit=1, check = is_not_me)

            #variable set up
            nummer = get_index()


            #assemble new message
            nachricht = remove_command(nachricht, 5)
            nachricht = message_start(nachricht, nummer)
            nachricht = message_end(nachricht, author)

            #send message
            nachricht = await message.channel.send(nachricht)
            increase_index()


            #add reactions
            await nachricht.add_reaction(yes_vote)
            await nachricht.add_reaction(no_vote)
            await nachricht.add_reaction(abstain_vote)
    



        #edit command
        if message.content.startswith('&edit ') or message.content.startswith('&Edit '):
        
            #variable set up
            args = nachricht.split(' ')
            index = str(args[1]) #get index
            isamendment = False


            #clean command + digit
            nachricht = remove_command(nachricht, 5)
            nachricht = clean_digits(nachricht)


            #search bill by index
            kanalhistory = client.get_channel(senatorial_voting) #replace
            messages = await kanalhistory.history(limit=40).flatten()
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
                            billnummer = message2[5]
                            billnummer = billnummer.strip('*')
                            isamendment = True
                        changes = message2
                        authorbill = message2[len(message2) -2]
            
            #clean changes
            changes = changes[:len(changes) -4]
            changestemp = ''
            for element in changes:
                changestemp = changestemp + element + ' '
            changes = changestemp
            

            #error messages
            if y == -1:
                await message.channel.send('Either no bill with that index in the last 40 messages or other invalid input.' + author)
                return
            if not authorbill == author:
                await message.channel.send('This is not your Bill. ' + author)
                return

            #assamble new message
            if isamendment == True:
                nachricht = '**Bill ' + str(index) + ':** Amendment to **Bill ' + str(billnummer) + '** ' + ('\r\n') + nachricht + ' '
            else:
                nachricht = message_start(nachricht, index)
            nachricht = message_end(nachricht, author)

            #edit message
            await messages[y].edit(content = nachricht)
            await kanal.send('Original wording: '+ ('\r\n') + '```' + changes + '```' + ('\r\n') + 'Success. ' + author)




        #option scenario
        if message.content.startswith('&option ') or message.content.startswith('&Option '):
        
            #deletes command message
            await message.channel.purge(limit=1, check = is_not_me)

            #variable set up
            args = nachricht.split(' ')
            amount = args[1] #get number
            if not is_number(amount):
                return
            amount = int(amount)
            nummer = get_index()


            #assemble new message
            nachricht = remove_command(nachricht, 7)
            nachricht = clean_digits(nachricht)
            nachricht = message_start(nachricht, nummer)
            nachricht = message_end(nachricht, author)

            #send message
            nachricht = await message.channel.send(nachricht)
            increase_index()


            #add reactions
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




        #amendment scenario
        if message.content.startswith('&amendment ') or message.content.startswith('&Amendment '):
            
            #deletes command message
            await message.channel.purge(limit=1, check = is_not_me)

            #variable set up
            args = nachricht.split(' ')
            billnummer = args[1] #get bill number
            if not is_number(billnummer):
                print(billnummer, '1')
                return
            billnummer = int(billnummer)
            nummer = get_index()


            #assemble new message
            nachricht = remove_command(nachricht, 10)
            nachricht = clean_digits(nachricht)
            nachricht = '**Bill ' + str(nummer) + ':** Amendment to **Bill ' + str(billnummer) + '** ' + ('\r\n') + nachricht + ' '
            nachricht = message_end(nachricht, author)

            #errors
            text = open('index.txt', 'r')
            check = int(text.read())
            text.close
            if check < billnummer:
                kanal = client.get_channel(senate)
                await kanal.send('''You can't amend a non-existant bill.''' + author)
                return

            #send message
            nachricht = await message.channel.send(nachricht)
            increase_index()


            #add reactions
            await nachricht.add_reaction(yes_vote)
            await nachricht.add_reaction(no_vote)
            await nachricht.add_reaction(abstain_vote)
        



        #amendment option
        if message.content.startswith('&amendmentoption ') or message.content.startswith('&Amendmentoption '):
            
            #deletes command message
            await message.channel.purge(limit=1, check = is_not_me)

            #variable set up
            args = nachricht.split(' ')
            billnummer = args[1] #get bill number
            if not is_number(billnummer):
                return
            billnummer = int(billnummer)
            amount = args[2] #get options amount
            if not is_number(amount):
                return
            amount = int(amount)
            nummer = get_index()


            #assemble new message
            nachricht = remove_command(nachricht, 16)
            nachricht = clean_digits(nachricht)
            nachricht = clean_digits(nachricht)
            nachricht = '**Bill ' + str(nummer) + ':** Amendment to **Bill ' + str(billnummer) + '** ' + ('\r\n') + nachricht + ' '
            nachricht = message_end(nachricht, author)

            #errors
            text = open('index.txt', 'r')
            check = int(text.read())
            text.close
            if check < billnummer:
                kanal = client.get_channel(senate)
                await kanal.send('''You can't amend a non-existant bill.''' + author)
                return
            
            #send message
            nachricht = await message.channel.send(nachricht)
            increase_index()

            #add reactions
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
        
        


        #edit bill numbers
        if message.content.startswith('&index ') or message.content.startswith('&Index '):
            
            #variable set up
            args = nachricht.split(' ')
            indexnew = args[1] #get newindex
            if not is_number(indexnew):
                await message.channel.send('Thats not a number. ' + author)
                return


            #edit index
            text = open('index.txt', 'w')
            text.write(str(int(indexnew) -1))
            text.close

            #response
            await message.channel.send('Succes, the next bill number will be: ' + indexnew + '. ' + author)









client.run('Nzc3ODY3NDAxNTQyMTA3MTQ4.X7JreA.D3zj_cgisn-qhafOBHZMTazZwqo')
