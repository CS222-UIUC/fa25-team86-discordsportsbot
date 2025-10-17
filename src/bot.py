# The main bot script

# We definitely need these at the very least
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import database session and initialization utilities
from db_skeleton import SessionLocal, init_db, Team, Player, Match, PlayerStat

#TODO: Need to add env folder

# Load ENV variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

# Fallback token (for testing only)
if not TOKEN:
    TOKEN = "REPLACE_WITH_YOUR_TOKEN"

# Set up Discord bot with message content intent enabled
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

client = MyClient(intents=intents)

# supposedly helps speed up testing?
MY_GUILD = discord.Object(id=1418704334941851722)


# This is temporary (borrowed) for testing if im doing any of this right - Rishi
@client.event
async def on_ready():
    print("We have successfully loggged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "sports" in message.content.lower():
        await message.channel.send("Did somebody say sports!?!")
        return

    if "football" in message.content.lower():
        await message.channel.send(
            "Erm, actually it's called soccer! "
            + "Unless you meant actual football in which case, carry on."
        )
        return

@bot.event
async def on_ready():
    """Runs once when the bot starts up."""
    try:
        # Initialize all DB tables (if not already created)
        await init_db()
        print("Database tables initialized.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
    try:
        # Test DB connection by running a simple SELECT query
        async with SessionLocal() as session:
            result = await session.execute(select(1))
            print("Database connection established.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    print(f"Logged in as {bot.user}")

@bot.command()
async def testdb(ctx):
    """Tests database connectivity by inserting and fetching sample data."""
    try:
        async with SessionLocal() as session:
            # Insert a dummy team record
            test_team = Team(
                id=9999,
                name="Test Team FC",
                league="Test League",
                country="Testland"
            )
            session.add(test_team)
            await session.commit()
            print(f"Added test team: {test_team.name}")

            # Fetch all teams from the DB
            result = await session.execute(select(Team))
            teams = result.scalars().all()
            
            team_names = [team.name for team in teams]

# On demand stats request
@client.tree.command()
# @app_commands.rename(full_name='full name')
@app_commands.describe(full_name="The full name of the player you want the stats of")
async def stats(interaction: discord.Interaction, full_name: str):
    """Current season statistics for a specific soccer player"""
    await interaction.response.send_message(
        "Here are the current stats of " + full_name + ": \n"
    )


# subscribe player command
@client.tree.command()
# @app_commands.rename(full_name='full name')
@app_commands.describe(full_name="The full name of the player you want to subscribe to")
async def subscribe_player(interaction: discord.Interaction, full_name: str):
    """Subscribes you to a player"""
    await interaction.response.send_message(
        "You have been subscribed to " + full_name + "!"
    )


# subscribe team command
@client.tree.command()
# @app_commands.rename(full_name='team name')
@app_commands.describe(full_name="The name of the team you want to subscribe to")
async def subscribe_team(interaction: discord.Interaction, full_name: str):
    """Subscribes you to a team"""
    await interaction.response.send_message(
        "You have been subscribed to " + full_name + "!"
    )


# unsubscribe player command
@client.tree.command()
# @app_commands.rename(full_name='full name')
@app_commands.describe(
    full_name="The full name of the player you want to unsubscribe from"
)
async def unsubscribe_player(interaction: discord.Interaction, full_name: str):
    """Unsubscribes you from a player"""
    await interaction.response.send_message(
        "You have been unsubscribed from " + full_name
    )


# unsubscribe team command
@client.tree.command()
# @app_commands.rename(full_name='team name')
@app_commands.describe(full_name="The name of the team you want to unsubscribe from")
async def unsubscribe_team(interaction: discord.Interaction, full_name: str):
    """Unsubscribes you from a team"""
    await interaction.response.send_message(
        "You have been unsubscribed from " + full_name
    )


# list subscriptions
@client.tree.command()
async def subscriptions(interaction: discord.Interaction):
    """Lists all subscribed players and teams"""
    await interaction.response.send_message(
        "Hi "
        + interaction.user.display_name
        + "!\n"
        + "Here are all of the players you are subscribed to: \n \n "
        + "Here are all of the teams you are subscribed to: \n "
    )


client.run(TOKEN)
        # Send results back to the Discord channel
        await ctx.send(
            f"Database test successful!\n"
            f"Total teams: {len(teams)}\n"
            f"Teams: {', '.join(team_names)}"
        )
        
    except Exception as e:
        # Catch and log any DB errors
        await ctx.send(f"Database test failed: {e}")
        print(f"Error in testdb: {e}")

# Zeeshan, we shoudln't be using !commands, we should use /commands
# also it doesn't make sense for users to be adding players to teams through the discord interface
# we should be handling that on the backend - Rishi
# @bot.command()
# async def addplayer(ctx, name: str, team_name: str):
#     """Adds a new player to an existing team."""
#     try:
#         async with SessionLocal() as session:
#             # Find the team the player should belong to
#             result = await session.execute(select(Team).where(Team.name == team_name))
#             team = result.scalar_one_or_none()
            
#             if not team:
#                 await ctx.send(f"Team '{team_name}' not found. Create it first with !testdb")
#                 return
            
#             # Create and insert a new player record
#             new_player = Player(
#                 name=name,
#                 team_id=team.id,
#                 position="Forward",
#                 age=25,
#                 nationality="Unknown"
#             )
#             session.add(new_player)
#             await session.commit()
            
#         await ctx.send(f"Added player '{name}' to team '{team_name}'")
        
#     except Exception as e:
#         await ctx.send(f"Failed to add player: {e}")
#         print(f"Error in addplayer: {e}")

bot.run(TOKEN)
