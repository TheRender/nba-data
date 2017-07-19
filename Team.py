# @type :: CLASS
# @class :: Team
# @author :: Steven Hanna
# @description :: Class to contain team management
# @end

import json
import requests

from Player import Player

class Team(object):

    # @type :: FUNC
    # @name :: __init__
    # @description :: Constructor for a team object
    # @param :: self - self representation
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
    def __init__(self, name, city, tricode, teamID, players, logo, nickname, seasonWins, seasonLosses, location, logs):
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
        self.nickname = nickname
        # Try to get an ID
        result = self.get_api_id()
        if result != None:
            self.id = result

        print("Getting Players")
        self.get_players()

    # @type :: FUNC
    # @name :: upload
    # @param :: self - self representation
    # @description :: Determines and executes whether to upload with our without api id
    def upload(self):
        if hasattr(self, "id"):
            self.upload_existing()
        else:
            self.upload_new()
            result = self.get_api_id()
            if result != None:
                self.id = result

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
        print(r)

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
        r = requests.get('https://therender-nba-api.herokuapp.com/team/exists/nbaid/' + self.teamID)
        r = r.json()
        if r["exists"] == False:
            return None
        else:
            return r["id"]

    # @type :: FUNC
    # @name :: get_players
    # @param :: self - self representation
    # @description :: Retrieves and creates player objects for this team
    # @end
    def get_players(self):
        print("API Call")
        print(self.teamID)
        r = requests.get('http://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=2016-17&TeamID=' + self.teamID)
        r = r.json()
        print("API Finished")
        rowSet = r["resultSets"]["rowSet"]
        playerObjects = []
        for x in rowSet:
            headshotURL = "http://stats.nba.com/media/players/230x185/" + x[12] + ".png"
            player = Player(x[12], x[3], headshotURL, self.name, self.teamID, x[4], x[5], 0, 0, 0, [])
            print(player.json_dump())
            player.upload()
            self.players.append(player.id)
