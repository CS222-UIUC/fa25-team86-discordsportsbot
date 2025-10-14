#The main bot script

# We definitely need these at the very least
import discord
from discord import app_commands

TOKEN = 'REPLACE WITH THE TOKEN FROM THE SERVER'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# This is temporary (borrowed) for testing if im doing any of this right
@client.event
async def on_ready():
    print('We have successfully loggged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello, {message.author.display_name}!')
        return

    if message.content.lower() == 'bye':
        await message.channel.send(f'See you later, {message.author.display_name}!')
        return

client.run(TOKEN)
