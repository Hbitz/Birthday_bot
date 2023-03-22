import discord
from config import config as CONFIG
from database_handler import *

# Set up intents for discord bot
my_intents = discord.Intents.default()  # Loads the default intents(permissions, basically)
my_intents.members = True  # Be able to see the members in the server, required to get ID to be able to DB uesrs
my_intents.message_content = True  # Allows bot to see the content of messages sent

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
    print(message)
    if message.author == client.user:  # If a text msg is sent by the bot, never do any more commands
        return

    print(message.content)
    # test msg
    if message.content.startswith('test'):
        return await message.channel.send('hello')

    # Use this command to get the ID for channel the msg is sent in.
    # You can use this to save the ID's to the config file.
    # We use a local config file to not expose our API keys, channel IDs and member IDs to the internet
    if message.content.startswith('channel'):
        channel = discord.utils.get(client.get_all_channels())
        channel_id = channel.id
        print(channel_id)
        return await message.channel.send('id for this channel is: ' + str(channel_id))


client.run(CONFIG['DISCORD']['CLIENT_TOKEN'])