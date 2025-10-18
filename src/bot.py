import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Import database functions
from database import initialize_database, test_database, add_player_to_team

#TODO: Need to add env folder

# Load ENV variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Fallback token (for testing only)
if not TOKEN:
    TOKEN = "REPLACE_WITH_YOUR_TOKEN"

# Set up Discord bot with message content intent enabled
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Runs once when the bot starts up."""
    init_status = await initialize_database()
    for message in init_status["messages"]:
        print(message)
    print(f"Logged in as {bot.user}")

@bot.command()
async def testdb(ctx):
    """Tests database connectivity by inserting and fetching sample data."""
    result = await test_database()
    
    if result["success"]:
        team_names = [team.name for team in result["teams"]]
        await ctx.send(
            f"Database test successful!\n"
            f"Total teams: {len(result['teams'])}\n"
            f"Teams: {', '.join(team_names)}"
        )
        print(result["message"])
    else:
        await ctx.send(result["message"])
        print(f"Error in testdb: {result['message']}")

@bot.command()
async def addplayer(ctx, name: str, team_name: str):
    """Adds a new player to an existing team."""
    result = await add_player_to_team(name, team_name)
    await ctx.send(result["message"])
    if not result["success"]:
        print(f"Error in addplayer: {result['message']}")

bot.run(TOKEN)
