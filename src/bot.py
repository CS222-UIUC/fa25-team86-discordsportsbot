import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import database session and initialization utilities
from db_skeleton import SessionLocal, init_db, Team, Player, Match, PlayerStat, Subscription

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

@bot.command()
async def addplayer(ctx, name: str, team_name: str):
    """Adds a new player to an existing team."""
    try:
        async with SessionLocal() as session:
            # Find the team the player should belong to
            result = await session.execute(select(Team).where(Team.name == team_name))
            team = result.scalar_one_or_none()
            
            if not team:
                await ctx.send(f"Team '{team_name}' not found. Create it first with !testdb")
                return
            
            # Create and insert a new player record
            new_player = Player(
                name=name,
                team_id=team.id,
                position="Forward",
                age=25,
                nationality="Unknown"
            )
            session.add(new_player)
            await session.commit()
            
        await ctx.send(f"Added player '{name}' to team '{team_name}'")
        
    except Exception as e:
        await ctx.send(f"Failed to add player: {e}")
        print(f"Error in addplayer: {e}")

@bot.command()
async def subscribe(ctx, *, team_name: str):
    """Subscribes the user to a team for updates."""
    try:
        async with SessionLocal() as session:
            # Find the team the user mentioned
            team_result = await session.execute(select(Team).where(Team.name.ilike(f"%{team_name}%")))
            team = team_result.scalar_one_or_none()

            if not team:
                await ctx.send(f"Sorry, I couldn't find a team named '{team_name}'.")
                return

            # Check if the user is already subscribed to this team
            user_id = ctx.author.id
            sub_result = await session.execute(
                select(Subscription).where(Subscription.user_id == user_id, Subscription.team_id == team.id)
            )

            if sub_result.scalar_one_or_none():
                await ctx.send(f"You are already subscribed to {team.name}!")
                return

            # Create and save the new subscription
            new_subscription = Subscription(user_id=user_id, team_id=team.id)
            session.add(new_subscription)
            await session.commit()

            await ctx.send(f"You are now subscribed to updates for {team.name}!")

    except Exception as e:
        await ctx.send("An error occurred while trying to subscribe. Please try again.")
        print(f"Error in !subscribe: {e}")

bot.run(TOKEN)
