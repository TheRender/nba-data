# @type :: CLASS
# @class :: Gamelog
# @author :: Steven Hanna
# @description :: Class to contain gamelog management
# @end

import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Gamelog(object):

    def __init__(self, playerID, gameID, minutes, points, rebounds, assists, steals, blocks, fieldGoalsMade, fieldGoalsAttempted, fieldGoalPercentage, threePointsMade, threePointsAttempted, threePointsPercentage, freeThrowsMade, freeThrowsAttempted, freeThrowsPercentage, fouls, plusMinus):
        self.playerID = playerID
        self.gameID = gameID
        self.minutes = minutes
        self.points = points
        self.rebounds = rebounds
        self.assists = assists
        self.steals = steals
        self.blocks = blocks
        self.fieldGoalsMade = fieldGoalsMade
        self.fieldGoalsAttempted = fieldGoalsAttempted
        self.fieldGoalPercentage = fieldGoalPercentage
        self.threePointsMade = threePointsMade
        self.threePointsAttempted = threePointsAttempted
        self.threePointsPercentage = threePointsPercentage
        self.freeThrowsMade = freeThrowsMade
        self.freeThrowsAttempted = freeThrowsAttempted
        self.freeThrowsPercentage = freeThrowsPercentage
        self.fouls = fouls
        self.plusMinus = plusMinus

    # @type :: FUNC
    # @name :: json_dump
    # @param :: self - self representation
    # @description :: Serialzes an object and dumps the result into JSON
    # @return :: A JSON representation of a gamelog object
    # @end
    def json_dump(self):
        return json.dumps(self, default=lambda x: x.__dict__)


    # @type :: FUNC
    # @name :: upload
    # @param :: self - self representation
    # @description :: Determines and executes whether to upload with our without api id
    def upload(self):
        logger.info("Uploading gamelog: " + str(self.playerID))
        if hasattr(self, "id"):
            self.upload_existing()
        else:
            self.upload_new()
            result = self.get_api_id()
            if result != None:
                self.id = result

    # @type :: FUNC
    # @name :: upload_new
    # @param :: self - self representation
    # @description :: Uploads a new gamelog
    # @end
    def upload_new(self):
        r = requests.post('https://therender-nba-api.herokuapp.com/gamelog/new', data=self.json_dump())

    # @type :: FUNC
    # @name :: upload_existing
    # @param :: self - self representation
    # @description :: Uploads an existing gamelog as an edit
    # @end
    def upload_existing(self):
        r = requests.post('https://therender-nba-api.herokuapp.com/gamelog/edit', data=self.json_dump())

    # @type :: FUNC
    # @name :: get_api_id
    # @param :: self
    # @returns :: False | the referenced API ID
    # @description :: Determines if the gamelog exists or not. If it does, it
    # supplies the API id
    # @end
    def get_api_id(self):
        r = requests.get('https://therender-nba-api.herokuapp.com/gamelog/exists/nbaid/' + str(self.gameID) + '/' + str(self.playerID))
        r = r.json()
        if r["exists"] == False:
            logger.info("Gamelog does not exist... Creating")
            logger.info("https://therender-nba-api.herokuapp.com/gamelog/exists/nbaid/" + str(self.gameID) + "/" + str(self.playerID))
            return None
        else:
            return r["id"]
