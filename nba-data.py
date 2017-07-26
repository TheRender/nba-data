# @type :: CLASS
# @class :: nba-data
# @author :: Steven Hanna
# @description :: The main workings of nba-data
# @end

import requests
import json
from Team import Team
from Gamelog import Gamelog
from Game import Game
import datetime
from multiprocessing.dummy import Pool as ThreadPool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

p = ThreadPool(16)

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
    logger.info("Starting teams")
    populate_team_basic()
    populate_team_season_record()
    upload_teams()
    get_current_games()
    p.close()
    p.join()

# @type :: FUNC
# @name :: populate_team_basic
# @description :: Populates basic information about teams
# @end
def populate_team_basic():
    try:
        r = requests.get('http://data.nba.net/data/10s/prod/v1/2017/teams.json')
        r = r.json()
        league = r["league"]
        standardArray = league["standard"]
        p.map(configure_team, standardArray)
    except ValueError, e:
        logger.error("Could not decode JSON object")
        logger.error(e)
        logger.error("Retrying")
        populate_team_basic()


def configure_team(t):
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
    logger.info("Uploading teams")
    teamsList = []
    for key, value in teams.iteritems():
        teamsList.append(value)
    p.map(upload_helper, teamsList)
    for x in teamsList:
        x.get_players()
    p.map(upload_helper, teamsList)

def upload_helper(x):
    logger.info("Uploading: " + x.name)
    x.upload()

# @type :: FUNC
# @name :: get_current_games
# @description :: gets the current games of the day, and uploads them
# @end
def get_current_games():
    logger.info("Getting current games")
    date = "20170207"
    # date = get_current_date_nba()
    r = requests.get("http://data.nba.net/data/10s/prod/v1/" + date + "/scoreboard.json")
    r = r.json()
    nbaGames = r["games"]
    games = []
    for x in nbaGames:
        logger.info("Game: " + x["gameId"])
        visitingTeamID = x["vTeam"]["teamId"]
        homeTeamID = x["hTeam"]["teamId"]
        logging.info("GAME ID's: " + str(homeTeamID) + " , " + str(visitingTeamID))
        games.append(Game(get_current_date(), x["gameId"], x["startTimeUTC"], x["clock"], x["period"]["current"], x["isBuzzerBeater"], x["period"]["isHalftime"], x["hTeam"]["score"], homeTeamID, x["hTeam"]["triCode"], x["vTeam"]["score"], visitingTeamID, x["vTeam"]["triCode"]))
    p.map(upload_game, games)

def upload_game(game):
    logger.info("Uploading game: " + str(game.gameID))
    game.upload()

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
    logger.info("Enter")
    team_api()
