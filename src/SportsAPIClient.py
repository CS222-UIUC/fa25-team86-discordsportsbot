
import aiohttp
import asyncio
import time
import json

# SPI_Football_key is required if you want to use it. Default Sports_DB_Key is 3. (I should probably be able to input keys but for now its fine for MVP)

API_FOOTBALL_KEY = "replace with your api key"
SPORTS_DB_KEY = "replace with your own api key"

SPORTS_DB_URL = f"https://www.thesportsdb.com/api/v1/json/{SPORTS_DB_KEY}"


# The class SportsAPIClient will be responsible for giving back the player info.
class SportsAPIClient:    
    
    #we will only have 1 session defined per server that is passed through the class rather than creating bunch of new ones
    def __init__(self, session):
        self.session = session
    
    async def get_player(self, player):
        # check for either apifootball/sports_db/or both? for now just using sports_DB
        async with self.session.get(f"{SPORTS_DB_URL}/searchplayers.php?p={player}") as response: 
            player_info = await response.json()
        
        # format json so only necessary information is sent and return        
        # TODO needs to only parse to return data we want either via parsing here/function/constructor 
                
        return player_info
    
    async def get_team(self, team):
        
        # check for either apifootball/sports_db or both? for now just using sports_DB
        async with self.session.get(f"{SPORTS_DB_URL}/searchteams.php?t={team}") as response:
            team_info = await response.json()
        
        # format json so only necessary information is sent 
        # TODO needs to only parse to return data we want either via parsing here/function/constructor  
        
        return team_info
    

# for testing for now
# async def main():
#     async with aiohttp.ClientSession() as session:
#         curr_session = SportsAPIClient(session)
#         test_player = "Danny_Welbeck"
#         test_team = "Arsenal"
        
#         player_info = await curr_session.get_player(test_player)
#         team_info = await curr_session.get_team(test_team)
#         print(player_info)
#         print(team_info)
# asyncio.run(main())