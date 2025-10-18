from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db_skeleton import SessionLocal, init_db, Team, Player, Match, PlayerStat

async def initialize_database():
    """Initialize the database and test the connection."""
    init_status = {"success": True, "messages": []}
    
    try:
        # Initialize all DB tables (if not already created)
        await init_db()
        init_status["messages"].append("Database tables initialized.")
    except Exception as e:
        init_status["success"] = False
        init_status["messages"].append(f"Database initialization failed: {e}")
        return init_status
    
    try:
        # Test DB connection by running a simple SELECT query
        async with SessionLocal() as session:
            result = await session.execute(select(1))
            init_status["messages"].append("Database connection established.")
    except Exception as e:
        init_status["success"] = False
        init_status["messages"].append(f"Database connection failed: {e}")
    
    return init_status

async def test_database():
    """Test database connectivity by inserting and fetching sample data."""
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

            # Fetch all teams from the DB
            result = await session.execute(select(Team))
            teams = result.scalars().all()
            
            return {
                "success": True,
                "teams": teams,
                "message": f"Added test team: {test_team.name}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "teams": [],
            "message": f"Database test failed: {e}"
        }

async def add_player_to_team(name: str, team_name: str):
    """Add a new player to an existing team."""
    try:
        async with SessionLocal() as session:
            # Find the team the player should belong to
            result = await session.execute(select(Team).where(Team.name == team_name))
            team = result.scalar_one_or_none()
            
            if not team:
                return {
                    "success": False,
                    "message": f"Team '{team_name}' not found. Create it first with !testdb"
                }
            
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
            
            return {
                "success": True,
                "message": f"Added player '{name}' to team '{team_name}'"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to add player: {e}"
        }