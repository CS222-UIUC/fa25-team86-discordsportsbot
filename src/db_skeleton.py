from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

#Base class for SQLAlchemy
#SQLAlchemy is somewhat new to me so if I slip up and put a VARCHAR somewhere I shouldn't you're allowed to yell at me 
#but be nice about it please
Base = declarative_base()

### ------------------------------------------------------------ FOOTBALL DATA ------------------------------------------------------------------------------------
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
    subscriptions = relationship("TeamSubscription", back_populates="team") #Discord members who follow this team

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
    lifetime_stats = relationship("LifetimeStat", uselist=False, back_populates="player")  # One-to-One
    subscriptions = relationship("PlayerSubscription", back_populates="player")  # Discord members who follow this player

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
    lifetime_stats = relationship("LifetimeStat", uselist=False, back_populates="player", cascade="all, delete-orphan") #use-list ensures the relation is one to one i believe
    #creates a lifetimestat object that hopefully is always pointed to by one player. bidirectional because it's more convenient to have
    #everything point to playerstat over going to lifetime stat separately. 


class LifetimeStat(Base):
    __tablename__ = "lifetime_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), unique=True, nullable=False)
    total_goals = Column(Integer, default=0)
    total_assists = Column(Integer, default=0)
    total_yellow_cards = Column(Integer, default=0)
    total_red_cards = Column(Integer, default=0)
    total_minutes_played = Column(Integer, default=0)
    appearances = Column(Integer, default=0)
    player = relationship("Player", back_populates="lifetime_stats")
    #the way this object is set-up we can either handle aggregation ourselves or do API calls on this. One
    #is faster than the other but is also a lot easier to mess up haha

#THINGS TO CONSIDER: How are our API calls going to be handled for these objects?

### ------------------------------------------------------------ DISCORD TRACKING ------------------------------------------------------------------------------------
#not the right amount of hyphens surely. it's fine we'll live. 

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True) #our internal primary key. if we want to finagle this into being the discord_id we can do that too i think
    discord_id = Column(String(50), unique=True, nullable=False) #discord key 
    username = Column(String(100))
    timezone = Column(String(50)) #transforms on the date-time for matches 
    player_subscriptions = relationship("PlayerSubscription", back_populates="member")
    team_subscriptions = relationship("TeamSubscription", back_populates="member") #storing these separately because it gets messy
    #haha messi
    #otherwise

class PlayerSubscription(Base):
    __tablename__ = "player_subscriptions"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    notify_on_goal = Column(Integer, default=1)
    notify_on_card = Column(Integer, default=1)
    notify_on_match = Column(Integer, default=0) #things that i think are worth having the subscribe call for
    #could extend into fouls etc (but we said we don't want to do haterisms haha)
    member = relationship("Member", back_populates="player_subscriptions")
    player = relationship("Player", back_populates="subscriptions")
    __table_args__ = (UniqueConstraint('member_id', 'player_id', name='_member_player_uc'),) #no duplicate subs 
    #also idk if naming convention is _name for the name field here or if you have to do that but 
    #every example i've found does it like this. so i guess we'll be a goody two shoes about it. 


class TeamSubscription(Base):
    __tablename__ = "team_subscriptions"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    notify_on_goal = Column(Integer, default=0)
    notify_on_match = Column(Integer, default=1)
    #don't think we can track team getting carded unless we are looking at 
    #players and then mapping that to teams and then mapping that back here
    #APIs don't seem to offer aggregate team card trackers I think. Either way, maybe a stretch feature? 
    member = relationship("Member", back_populates="team_subscriptions")
    team = relationship("Team", back_populates="subscriptions")
    __table_args__ = (UniqueConstraint('member_id', 'team_id', name='_member_team_uc'),) #no duplicate subs





