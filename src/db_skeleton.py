from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

#Base class for SQLAlchemy
#SQLAlchemy is somewhat new to me so if I slip up and put a VARCHAR somewhere I shouldn't you're allowed to yell at me 
#but be nice about it please
Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)  #APIs we are pulling from presumably have each team mapped to a unique ID. 
    #If this is hard to verify, might want to change how we do this
    name = Column(String(100), nullable=False)
    league = Column(String(100)) #100 is overkill but idk there might be leagues in this world that are overly wordy. Like me!
    country = Column(String(50)) #League and Country being here is quite expansive; if we feel pressed for time we might just restrict
    #ourselves to the Big 6 leagues (5 + UCL) (sorry to people who care about Real Betis B Team I guess)
    players = relationship("Player", back_populates="team") #One to Many
    home_matches = relationship("Match", foreign_keys='Match.home_team_id', back_populates="home_team") 
    #home-away classification is not as important but in some leagues it makes a difference. easily editable 
    #if we decide to do so though.
    away_matches = relationship("Match", foreign_keys='Match.away_team_id', back_populates="away_team") 

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True) #Same note as TeamID.
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id')) #Many to One 
    position = Column(String(50)) #50 is a bit much lol but IDK if we'll list abbreviations or full positionings (i.e. FB vs FullBack).
    age = Column(Integer)
    nationality = Column(String(50))
    team = relationship("Team", back_populates="players")
    stats = relationship("PlayerStat", back_populates="player") 

#My thinking is that since we're doing live updates each Player gets assigned a PlayerStat object for each match, so it's 
#One to Many here, instead of tracking lifetime stats. If we do lifetime stats they would go here in this table and be 
#updated as PlayerStat objects are updated. That would require just a little more finagling which 
#I can take a look at later. What we then need to think of is how we are IDing PlayerStat objects--- 
#something to consider when API wrangling.

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    date = Column(Date)
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    stats = relationship("PlayerStat", back_populates="match") #leads to every PlayerStat object with this MatchID (One to Many)

class PlayerStat(Base):
    __tablename__ = "player_stats"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    match_id = Column(Integer, ForeignKey('matches.id'))
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    player = relationship("Player", back_populates="stats")
    match = relationship("Match", back_populates="stats") #yapped enough on the other ones that hopefully this object is clear. 