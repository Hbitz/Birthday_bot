import discord
from config import config as CONFIG
from database_handler import *
import datetime
import aiocron


# Set up intents for discord bot
my_intents = discord.Intents.default()  # Loads the default intents(permissions, basically)
my_intents.members = True  # Be able to see the members in the server, required to get ID to be able to DB uesrs
my_intents.message_content = True  # Allows bot to see the content of messages sent

# my_intents.all()

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
    global all_birthdays
    if message.author == client.user:  # If a text msg is sent by the bot, never do any more commands
        return

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
        bdays = all_birthdays
        s = ''
        for bday in bdays:
            s += str(bday) + '\n'
        return await message.channel.send(s)

    if message.content.startswith('!month'):  # If we want to see all birthdays in a month
        months = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        } # Support for both English and Swedish. This is high quality coding.
        swedish_months = {
            'Januari': '01',
            'Februari': '02',
            'Mars': '03',
            'April': '04',
            'Maj': '05',
            'Juni': '06',
            'Juli': '07',
            'Augusti': '08',
            'September': '09',
            'Oktober': '10',
            'November': '11',
            'December': '12'
        }
        msg= message.content[7:].capitalize()

        month_number = 0  # Set a default value
        # Now overwrite value depending on month.  Sets a value in string format '01'
        if msg in months:
            month_number = months[msg]
        elif msg in swedish_months:
            month_number = swedish_months[msg]
        else:  # If the input is not a valid month, stop function here and notify user
            return await message.channel.send('That is not a valid month')

        results = load_specific_month(month_number)  # Now load all birthdays for that month
        s = "ID\tBirthday\tGift\tReminder\tName\n"  # Let's create a nice format/table to display all results
        # Todo - Explore string formatting with fixed lengths.
        for r in results:
            s += f'{r[0]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[1]}\n'  # Name at end, so the rest if formatted better.
        return await message.channel.send(s)

    if message.content.startswith('!delete'):  # Delete alert based on ID
        _, bday_id = message.content.split(' ')  # Split msg on ' '.
        # _ = "!delete", id = <our_input>

        # Verify input id
        try:
            bday_id = int(bday_id)
        except ValueError:
            return await message.channel.send('You need to enter a numerical value.')

        s = delete_from_db(bday_id)
        all_birthdays = load_all_from_db()  # Update global variable so we keep using fresh data
        return await message.channel.send(f'Deleted:  {s}')

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
        all_birthdays = load_all_from_db()  # Update global variable with fresh data
        return await message.channel.send('Data was clean and was hopefully saved to db')  # Todo reponse of result

    # This is using same logic as !add, got much duplicated code atm
    if message.content.startswith('!edit'):
        msg = message.content[6:]  # Remove the "!edit " for easier handling.
        bday_id, name, date, *extra = msg.split(' ')

        try:
            bday_id = int(bday_id)
        except ValueError:
            return await message.channel.send('The ID must be a numerical value.')

        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            return await message.channel.send('The date format is not correct')

        # set default values
        gift = 'No'
        reminder = 0

        # Verify and handle extra data, if any, to overwrite the default values
        if len(extra) > 0:
            gift = extra[0].capitalize()  # Gets the first element of our extra data
            if gift != 'Yes' and gift != 'No':
                return await message.channel.send(f'Gift should be a "Yes/No" value. You wrote "{gift}".')
            if len(extra) > 1:  # If user also set a reminder of x days ahead
                try:
                    reminder = int(extra[1])
                except ValueError:
                    return await message.channel.send(
                        f'Reminder(days ahead) should be numerical value. You entered {extra[1]}')

        # Save our data to the database
        update_alert(bday_id, name, date, gift=gift, reminder=reminder)
        all_birthdays = load_all_from_db()  # Update global variable with fresh data from db
        return await message.channel.send('Data was clean and was hopefully updated to db')

    if message.content.startswith('!test'):
        await send_notification()


async def send_notification(message=None):
    # Update global variables(should be done in cronjob later on)
    all_birthdays = load_all_from_db()

    # Setup
    today = datetime.datetime.today()  # Get string of today in YYYY-mm-dd format

    user = client.get_user(CONFIG['DISCORD']['MY_USER']['ID'])
    s = ''

    for bday in all_birthdays:
        # Create datetime object from the string value
        bday_date = datetime.datetime.strptime(bday[2], '%Y-%m-%d')  # strptime to format string to datetime object

        # Let's see how many days it is until their next birthdays
        next_birthday = bday_date.replace(year=today.year)  # Replace birthyear with current year
        if next_birthday < today:  # If birthday has already been this year
            next_birthday = next_birthday.replace(year=today.year + 1)

        # Datetime rounds down, so 23:59:59 in the future still only counts as 0, which is today.
        # So we add + 1 to get the next day.
        days_until_birthday = (next_birthday - today).days + 1




        ## Todo - Temporary solution.
        # We both need to check if a birthday is today, or if it's reminder(of next year) should be sent.
        # The first check is obvious(Now implemented via str of datetimeboject[5:10] to get the "mm-dd".
        # The second would be if it's December 25st & you have a reminder for your friend's birthday in 10 days(next year).
        if str(bday_date)[5:10] == str(datetime.datetime.today())[5:10]:
            years = next_birthday.year - bday_date.year  # Calculate how many years old they are turning
            s += str(f'{bday[1]} is turning {years} today.')
            if bday[3] == 'Yes':
                s += ' Remember to get a gift.'
            s += f' [ID:{bday[0]}]\n'


        # Reminder: A bday is currently a list of [id, name, date, gift, reminder)
        # Todo - Lots of duplicated code. Can this be reduced?
        ###print('\n', bday, ', days til bday: ', days_until_birthday, ':    ', end='')
        elif days_until_birthday == 0 or days_until_birthday == -1:  # Check if someone has their birthday today. Todo: Is "-1" redundant?

            years = next_birthday.year - bday_date.year  # Calculate how many years old they are turning
            s += str(f'{bday[1]} is turning {years} today.')
            if bday[3] == 'Yes':
                s += ' Remember to get a gift.'
            s += f' [ID:{bday[0]}]\n'
        elif days_until_birthday == int(bday[4]):  # Check if we have an alert set up X days in advance for the birthday.
            years = next_birthday.year - bday_date.year  # Calculate how many years old they are turning
            s += str(f'{bday[1]} is turning {years} in {bday[4]} days.')
            if bday[3] == 'Yes':
                s += ' Remember to get a gift.'
            s += f' [ID:{bday[0]}]\n'

    msg_to_send = s
    print(msg_to_send)

    if msg_to_send:  # Check if it's not empty
        channel = await user.create_dm()  # Create DM with user
        return await channel.send(msg_to_send)  # Send our message
    else:
        print('Local temporary print - no alerts at this time~~')


async def update_globals():
    global all_birthdays
    all_birthdays = load_all_from_db()


# A cronjob is something that is run automatically at set intervals.
# https://crontab.guru/ for more info on format
# "minute hour day(month) month day(week)"
# "0 9 * * *" means to run this at 9:00 every day
@aiocron.crontab('0 9 * * *', start=False)
async def cronjob1():
    await update_globals()  # Update globals.   # todo Do we need this? We could just update on every change in db?
    await send_notification()  # Send notifications

cronjob1.start()

client.run(CONFIG['DISCORD']['CLIENT_TOKEN'])