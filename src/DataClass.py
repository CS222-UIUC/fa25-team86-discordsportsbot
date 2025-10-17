# the code will contain bunch of dictionary that will be useful around the codes to use/convert # These are the things we only need
# better way to do this is to initalize everything to None instead and handle error? but for now i think empty string will be fine for safe initialization
  
class Player:
    
    def __init__(self, id = "", name = "", team_id = "", position = "", age = "", nationality = "", team = "", stats = ""):
        self.id = id
        self.name = name
        self.team_id = team_id
        self.position = position
        self.age = age
        self.nationality = nationality
        self.team = team
        self.stats = stats
    
    def from_api_json(self, dictionary):
        # TODO
        return self
        

#same as above, I should initalize them to none but for now before tests, this shall be fine.
class Team:
    
    def __init__(self, id="", name="", league="", country = "", players=[], home_matches="",away_matches=""):
        self.id = id
        self.name = name
        self.league = league
        self.country = country
        self.players = players
        self.home_matches = home_matches
        self.away_matches = away_matches
        
    def from_api_json(self, dictionary):
        # TODO
        return self