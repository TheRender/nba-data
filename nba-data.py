# @type :: CLASS
# @class :: nba-data
# @author :: Steven Hanna
# @description :: The main workings of nba-data
# @end

import requests
import json
from Team import Team
from Gamelog import Gamelog
import datetime

# @type :: VAR
# @name :: teams
# @description :: Main global variable to hold teams
# @end
teams = {}

# @type :: FUNC
# @name :: team_api
# @description :: The main delegate function that calls other api functions for teams
# @end
def team_api():
    populate_team_basic()
    populate_team_season_record()
    # get_current_games()
    upload_teams()

# @type :: FUNC
# @name :: populate_team_basic
# @description :: Populates basic information about teams
# @end
def populate_team_basic():
    r = requests.get('http://data.nba.net/data/10s/prod/v1/2017/teams.json')
    r = r.json()
    league = r["league"]
    standardArray = league["standard"]
    for t in standardArray:
        logo = "http://stats.nba.com/media/img/teams/logos/" + t["teamId"] + "_logo.svg"
        team = Team(t["fullName"], t["city"], t["tricode"], t["teamId"], [], logo, t["nickname"], 0, 0, t["confName"], [])
        teams[team.teamID] = team

# @type :: FUNC
# @name :: populate_team_season_record
# @description :: Populates season record information for teams
# @end
def populate_team_season_record():
    r = requests.get('http://data.nba.net/data/10s/prod/v1/current/standings_conference.json')
    r = r.json()
    league = r["league"]
    east = league["standard"]["conference"]["east"]
    west = league["standard"]["conference"]["west"]
    combined = east + west
    for x in combined:
        tID = x["teamId"]
        print(tID in teams.keys())
        if tID in teams.keys():
            team = teams[tID]
            team.seasonWins = x["win"]
            team.seasonLosses = x["loss"]
            teams[tID] = team

# @type :: FUNC
# @name :: upload_teams
# @description :: Uploads all of the teams
# @end
def upload_teams():
    for key, value in teams.iteritems():
        value.upload()
        value.get_players()
        value.upload()


# @type :: FUNC
# @name :: get_current_games
# @description :: gets the current games of the day, and uploads them
# @end
def get_current_games():
    print("Getting current games")
    date = "20170207"
    # date = get_current_date_nba()
    r = requests.get("http://data.nba.net/data/10s/prod/v1/" + date + "/scoreboard.json")
    r = r.json()
    nbaGames = r["games"]
    for x in nbaGames:
        print(x)
        gameID = x["gameId"]
        visitingTeam = x["vTeam"]
        homeTeam = x["hTeam"]
        minutes = int(x["gameDuration"]["hours"]) * 60 + int(x["gameDuration"]["minutes"])
        score = homeTeam["score"] + "-" + visitingTeam["score"]
        log1 = Gamelog(get_current_date(), "", homeTeam["teamId"], "", visitingTeam["teamId"], score, str(minutes), homeTeam["score"], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        log2 = Gamelog(get_current_date(), "", visitingTeam["teamId"], "", homeTeam["teamId"], score, str(minutes), visitingTeam["score"], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        id1 = log1.teamID
        id2 = log2.teamID
        if id1 in teams.keys():
            teams[id1].logs.append(log1.id)
        if id2 in teams.keys():
            teams[id2].logs.append(log2.id)

# @type :: FUNC
# @name :: get_current_date_nba
# @description :: Get's the current date just the way the nba likes it
# @return :: String - string representation of the date
# @end
def get_current_date_nba():
    now = datetime.datetime.now()
    currentYear = int(now.year)
    currentMonth = int(now.month)
    currentDay = int(now.day)
    if currentDay < 10:
        currentDay = "0" + str(currentDay)
    if currentMonth < 10:
        currentMonth = "0" + str(currentMonth)
    return str(currentYear) + str(currentMonth) + str(currentDay)

# @type :: FUNC
# @name :: get_current_date
# @description :: Gets the current general date
def get_current_date():
    now = datetime.datetime.now()
    date = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    return date

if __name__ == '__main__':
    # We going to do some shit here
    team_api()
