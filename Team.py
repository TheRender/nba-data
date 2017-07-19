# @type :: CLASS
# @class :: Team
# @author :: Steven Hanna
# @description :: Class to contain team management
# @end

import json
import requests

class Team(object):

    # @type :: FUNC
    # @name :: __init__
    # @description :: Constructor for a team object
    # @param :: self - self representation
    # @param :: apiID - the id associated with our api
    # @param :: name - the name of the team
    # @param :: city - the city the team is located in
    # @param :: tricode - the tricode for the team
    # @param :: teamID - the teamID that the nba assigns
    # @param :: players - the array of player id's in association with our API
    # @param :: logo - a url link to the team logo
    # @param :: seasonWins = number of season wins
    # @param :: seasonLosses - number of season losses
    # @param :: location - the location that the team is in
    # @param :: logs - an array of log id's in association with our API
    # @end
    def __init__(self, apiID, name, city, tricode, teamID, players, logo, seasonWins, seasonLosses, location, logs):
        self.id = apiID
        self.name = name
        self.city = city
        self.tricode = tricode
        self.teamID = teamID
        self.players = players
        self.logo = logo
        self.seasonWins = seasonWins
        self.seasonLosses = seasonLosses
        self.location = location
        self.logs = logs

    def upload(self):
        x = json.dumps(self, default=lambda x: x.__dict__)
        print(x)

    def get_api_id(self):
        # r = requests.get('https://nba-api.therendersports.com/team/exists/nbaid/' + self.teamID)
        r = requests.get('https://therender-nba-api.herokuapp.com/team/exists/nbaid/' + self.teamID)
        # r = requests.get('https://therender-nba-api.herokuapp.com/teams')
        if r["exists"] == False:
            print("FALSE")
        else:
            print("TRUE")
        print(r.json())


x = Team("123", "Test", "Test", "Test", "Test", ["Test"], "Test", "Test", "Test", "Test", ["Test"])
x.get_api_id()
