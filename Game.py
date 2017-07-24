# @type :: CLASS
# @class :: Game
# @author :: Steven Hanna
# @description :: Class to mange games
# @end

import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Game(object):

    # @type :: FUNC
    # @name :: __init__
    # @description :: Constructor for a game object
    # @param :: self - self representation
    # @param :: date - date of the game
    # @param :: gameID - game ID
    # @param :: startTime - game start time
    # @param :: clock - current game clock
    # @param :: quarter - current quarter
    # @param :: isBuzzerBeater - If the game was a buzzer beater
    # @param :: isHalfTime - If it is halftime
    # @param :: homeTeamScore - The hometeam score
    # @param :: homeTeamID - The home team gameID
    # @param :: homeTriCode - The home team tricode
    # @param :: awayTeamScore - The away team score
    # @param :: awayTeamID - The away team id
    # @param :: awayTriCode - The away team tricode
    # @param :: homePlayers - The array of home players
    # @param :: awayPlayers - The array of away players
    def __init__(self, date, gameID, startTime, clock, quarter, isBuzzerBeater, isHalfTime, homeTeamScore, homeTeamID, homeTriCode, awayTeamScore, awayTeamID, awayTriCode):
        logger.info("Creating game: " + str(gameID))
        # TODO :: Convert teamID's to our db ID's
        self.date = date
        self.gameID = gameID
        self.startTime = startTime
        self.clock = clock
        self.quarter = quarter
        self.isBuzzerBeater = isBuzzerBeater
        self.isHalfTime = isHalfTime
        self.homeTeamScore = homeTeamScore
        self.homeTeamID = homeTeamID
        self.homeTriCode = homeTriCode
        self.awayTeamScore = awayTeamScore
        self.awayTeamID = awayTeamID
        self.awayTriCode = awayTriCode
        self.homePlayers = []
        self.awayPlayers = []
        # Try to get an ID
        self.get_player_logs()
        result = self.get_api_id()
        if result != None:
            self.id = result

    # @type :: FUNC
    # @name :: upload
    # @param :: self - self representation
    # @description :: Determines and executes whether to upload with our without api id
    def upload(self):
        logger.info("Uploading: " + str(self.gameID))
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
    # @return :: A JSON representation of a game object
    # @end
    def json_dump(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    # @type :: FUNC
    # @name :: upload_new
    # @param :: self - self representation
    # @description :: Uploads a new game
    # @end
    def upload_new(self):
        logger.info("Uploading new: " + str(self.gameID))
        r = requests.post('https://therender-nba-api.herokuapp.com/game/new', data=self.json_dump())
        print(r)

    # @type :: FUNC
    # @name :: upload_existing
    # @param :: self - self representation
    # @description :: Uploads an existing team as an edit
    # @end
    def upload_existing(self):
        logger.info("Uploading existing: " + str(self.gameID))
        r = requests.post('https://therender-nba-api.herokuapp.com/game/edit', data=self.json_dump())

    # @type :: FUNC
    # @name :: get_api_id
    # @param :: self
    # @returns :: False | the referenced API ID
    # @description :: Determines if the team exists or not. If it does, it
    # supplies the API id
    # @end
    def get_api_id(self):
        r = requests.get('https://therender-nba-api.herokuapp.com/game/exists/nbaid/' + self.gameID)
        r = r.json()
        if r["exists"] == False:
            return None
        else:
            return r["id"]

    def get_player_logs(self):
        logger.info("Getting player logs: " + str(self.gameID))
        r = requests.get('http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2016/scores/gamedetail/' + self.gameID + '_gamedetail.json')
        r = r.json()
        game = r["g"]
        visitingData = game["vls"]["pstsg"]
        homeData = game["hls"]["pstsg"]
        for player in visitingData:
            pid = get_player_id(player["pid"])
            self.awayPlayers.append(pid)
        for player in homeData:
            pid = get_player_id(player["pid"])
            self.homePlayers.append(pid)


# @type :: FUNC
# @name :: get_player_id
# @param :: nbaID - the player nbaid to look up
# @description :: Check and return the player's db
# @return :: None or string id
# @end
def get_player_id(nbaID):
    logger.info("Getting player ID: " + str(nbaID))
    r = requests.get('https://nba-api.therendersports.com/player/exists/nbaID/' + str(nbaID))
    r = r.json()
    if r["exists"] is True:
        return r["id"]
    else:
        return None
