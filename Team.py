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
        # self.id = apiID
        self.name = name
        self.city = city
        self.tricode = tricode
        self.players = players
        self.logo = logo
        self.teamID = teamID
        self.seasonWins = seasonWins
        self.seasonLosses = seasonLosses
        self.location = location
        self.logs = logs
        # Try to get an ID
        if apiID == None:
            result = self.get_api_id()
            if result != None:
                self.id = result

    def upload(self):
        x = json.dumps(self, default=lambda x: x.__dict__)
        print(x)

    # @type :: FUNC
    # @name :: json_dump
    # @param :: self - self representation
    # @description :: Serialzes an object and dumps the result into JSON
    # @return :: A JSON representation of a team object
    # @end
    def json_dump(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    # @type :: FUNC
    # @name :: upload_new
    # @param :: self - self representation
    # @description :: Uploads a new team
    # @end
    def upload_new(self):
        r = requests.post('https://therender-nba-api.herokuapp.com/team/new', data=self.json_dump())

    # @type :: FUNC
    # @name :: upload_existing
    # @param :: self - self representation
    # @description :: Uploads an existing team as an edit
    # @end
    def upload_existing(self):
        r = requests.post('https://therender-nba-api.herokuapp.com/team/edit', data=self.json_dump())

    # @type :: FUNC
    # @name :: get_api_id
    # @param :: self
    # @returns :: False | the referenced API ID
    # @description :: Determines if the team exists or not. If it does, it
    # supplies the API id
    # @end
    def get_api_id(self):
        # r = requests.get('https://nba-api.therendersports.com/team/exists/nbaid/' + self.teamID)
        r = requests.get('https://therender-nba-api.herokuapp.com/team/exists/nbaid/' + self.teamID)
        # r = requests.get('https://therender-nba-api.herokuapp.com/teams')
        r = r.json()
        if r["exists"] == False:
            return None
        else:
            return r["id"]

x = Team(None, "Test", "Test", "Test", "Test", ["Test"], "http://google.com", 0, 0, "Test", ["Test"])
# x.upload_new()
