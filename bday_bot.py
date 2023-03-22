import discord
from config import config as CONFIG
from database_handler import *
import datetime


# Set up intents for discord bot
my_intents = discord.Intents.default()  # Loads the default intents(permissions, basically)
my_intents.members = True  # Be able to see the members in the server, required to get ID to be able to DB uesrs
my_intents.message_content = True  # Allows bot to see the content of messages sent

my_intents.all()

client = discord.Client(intents=my_intents)

# global variables
all_birthdays = load_all_from_db()


@client.event
async def on_ready():  # When bot is started
    channel = client.get_channel(CONFIG['DISCORD']['CHANNEL_IDS']['Testkanal'])  # ID for channel "testkanal" in my server, which is retrieved from the config file
    print('We logged in as {0.user}'.format(client))
    await channel.send('Birthday bot woke up!')


# This function runs every time there's a new message in any of the channel the bot has access to
@client.event
async def on_message(message):
    if message.author == client.user:  # If a text msg is sent by the bot, never do any more commands
        return

    #print(message.content)
    # test msg
    if message.content.startswith('test'):
        return await message.channel.send('hello')

    # Use this command to get the ID for channel the msg is sent in.
    # You can use this to save the ID's to the config file.
    # We use a local config file to not expose our API keys, channel IDs and member IDs to the internet
    if message.content.startswith('!channel'):
        channel = discord.utils.get(client.get_all_channels())
        channel_id = channel.id
        print(channel_id)
        return await message.channel.send('id for this channel is: ' + str(channel_id))

    # Simple way to get user information, which is needed when sending a DM
    if message.content.startswith('!user'):
        print(message)  # message countains lots of useful info, such as info about the message, the author, the server.
        # Could also be sent to channel, instead of being to console/terminal

    if message.content.startswith('!info'):
        s = 'Add alert: "Name date(yyyy-mm-dd) gift(yes/no) reminder(days ahead)"'
        s += 'Add example: "Friend 2000-01-01 yes 7'
        # Friend has birthday 01-01, you should get a gift, and you'll get a DM from bot 1 week in advance.
        return await message.channel.send(s)

    if message.content.startswith('!everybday'):
        #bdays = load_all_from_db()
        bdays = all_birthdays
        s = ''
        for bday in bdays:
            s += str(bday) + '\n'
        return await message.channel.send(s)

    if message.content.startswith('!delete'):  # Delete alert based on ID
        _, id = message.content.split(' ')  # Split msg on ' '.
        # _ = "!delete", id = <our_input>

        # Verify input id
        try:
            id = int(id)
        except ValueError:
            return await message.channel.send('You need to enter a numerical value.')

        s = delete_from_db(id)
        return await message.channel.send(f'Deleted: ', s)

    if message.content.startswith('!add'):
        msg = message.content[5:]  # Remove first 5 letters,"!add ", for convenience.
        if msg.count(' ') < 1:
            return await message.channel.send('Need at least a name and a date as input. Check "!info" if you need help.')
        name, date, *extra = msg.split(' ')  # Splits the msg into name, data(variables) & remaining data into *extra(list)
        # Name and date will always be mandatory, and then we'll have the extra data(optional) separately

        # Verify data types is correct
        try:  # Built-in function from datetime. Raises error if string isn't in "YYYY-MM-DD" format
            print(date)
            datetime.date.fromisoformat(date)
        except ValueError:  # Notify user of incorrect date format
            return await message.channel.send('The date format is not correct')

        # Set default values of variables
        gift = 'No'
        reminder = 0

        # Verify and handle extra data, if any, to overwrite the default values
        if len(extra) > 0:
            gift = extra[0].capitalize() # Gets the first element of our extra data
            if gift != 'Yes' and gift != 'No':
                return await message.channel.send(f'Gift should be a "Yes/No" value. You wrote "{gift}".')
            if len(extra) > 1: # If user also set a reminder of x days ahead
                try:
                    reminder = int(extra[1])
                except ValueError:
                    return await message.channel.send(f'Reminder(days ahead) should be numerical value. You entered {extra[1]}')

        # Save our data to the database
        save_to_db(name, date, gift=gift, reminder=reminder)
        return await message.channel.send('Data was clean and was hopefully saved to db')

    if message.content.startswith('!test'):
        await send_notification()




async def send_notification(message=None):
    # Setup
    today = datetime.datetime.today()  # Get string of today in YYYY-mm-dd format
    today_str = datetime.datetime.today().strftime('%Y-%m-%d')  # Get string of today in YYYY-mm-dd format

    #today2 = datetime.date.today()
    #print('today-',today, ',', type(today))
    user = client.get_user(CONFIG['DISCORD']['MY_USER']['ID'])
    s = ''

    #for bday in all_birthdays:
    #    s += str(bday)
    for bday in all_birthdays:
        '''
        # A birthday is currently a list of [id, name, date, gift, reminder)
        #bday_date = datetime.date() bday[2].strftime('')
        print()
        print(bday[2])
        print('today:', today, type(today))
        #bday_date = datetime.datetime.strftime(bday[2], '%Y-%m-%d')
        bday_date = datetime.datetime.strptime(bday[2], '%Y-%m-%d')
        #t3 = da
        #print(f'today % bday: {today} % {bday_date}')
        print('bday_date: ', bday_date, ',', type(bday_date))

        remaining_days = bday_date - today
        print(remaining_days)
        print(remaining_days.days)
        '''

        # Create datetime object from the string value
        bday_date = datetime.datetime.strptime(bday[2], '%Y-%m-%d')  # strptime to format string to datetime object

        # Let's see how many days it is until their next birthdays
        next_birthday = bday_date.replace(year=today.year)  # Replace birthyear with current year
        if next_birthday < today:  # If birthday has already been this year
            next_birthday = next_birthday.replace(year=today.year + 1)
        # Datetime rounds down, so a birthday in 23:59:59 counts as 0, which is today. So we add + 1
        days_until_birthday = (next_birthday - today).days + 1
        print(days_until_birthday)

        if days_until_birthday == 0:
            s += str(bday)
            print('today note', str(bday))
        elif days_until_birthday == 0 + int(bday[4]):
            s += str(bday)
            print('reminder note')


    msg_to_send = s
    print(msg_to_send)

    #channel = await user.create_dm()  # Create DM with user
    #await channel.send(s)  # Send our message


client.run(CONFIG['DISCORD']['CLIENT_TOKEN'])