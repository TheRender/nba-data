# @type :: CLASS
# @class :: Player
# @author :: Steven Hanna
# @description :: Class to contain player management
# @end

import json
import requests

class Player(object):

    # @type :: FUNC
    # @name :: __init__
    # @description :: Constructor for a player object
    # @param :: self - self representation
    # @param :: playerID - the playerID that the nba assigns
    # @param :: name - the name of the player
    # @param :: headshotURL - the url for the headshot pic of the player
    # @param :: teamID - the teamID that the nba assigns
    # @param :: teamName - the name of the team that the player is on
    # @param :: jerseyNumber - the jersey number of the player
    # @param :: position - the position of the player
    # @param :: careerPPG - the careerPPG of the player
    # @param :: careerRPG - the careerRPG of the player
    # @param :: careerAPG - the careerAPG of the player
    # @param :: stats - an array of stats id's in association with our API
    # @end
    def __init__(self, playerID, name, heashotURL, teamName, teamID, jerseyNumber, position, careerPPG, careerRPG, careerAPG, stats):
        self.name = name
        self.playerID = playerID
        self.heashotURL = heashotURL
        self.teamName = teamName
        self.teamID = teamID
        self.jerseyNumber = jerseyNumber
        self.position = position
        self.careerPPG = careerPPG
        self.careerRPG = careerRPG
        self.careerAPG = careerAPG
        self.stats = []
        # Try to get an ID
        result = self.get_api_id()
        if result != None:
            self.id = result


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
    # @return :: A JSON representation of a player object
    # @end
    def json_dump(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    # @type :: FUNC
    # @name :: upload_new
    # @param :: self - self representation
    # @description :: Uploads a new player
    # @return :: the player ID associated with our db
    # @end
    def upload_new(self):
        r = requests.post('https://therender-nba-api.herokuapp.com/player/new', data=self.json_dump())

    # @type :: FUNC
    # @name :: upload_existing
    # @param :: self - self representation
    # @description :: Uploads an existing player as an edit
    # @end
    def upload_existing(self):
        r = requests.post('https://therender-nba-api.herokuapp.com/player/edit', data=self.json_dump())

    # @type :: FUNC
    # @name :: get_api_id
    # @param :: self
    # @returns :: False | the referenced API ID
    # @description :: Determines if the player exists or not. If it does, it
    # supplies the API id
    # @end
    def get_api_id(self):
        r = requests.get('https://therender-nba-api.herokuapp.com/player/exists/nbaid/' + self.teamID)
        r = r.json()
        if r["exists"] == False:
            return None
        else:
            return r["id"]
