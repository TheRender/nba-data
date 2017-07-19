# @type :: CLASS
# @class :: nba-data
# @author :: Steven Hanna
# @description :: The main workings of nba-data
# @end

import requests
import json
from Team import Team

teams = {}

# @type :: FUNC
# @name :: team_api
# @description :: The main delegate function that calls other api functions for teams
# @end
def team_api():
    populate_team_basic()
    populate_team_season_record()
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

if __name__ == '__main__':
    # We going to do some shit here
    team_api()
