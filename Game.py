# @type :: CLASS
# @class :: Game
# @author :: Steven Hanna
# @description :: Class to mange games
# @end

import json
import requests
import logging
from multiprocessing.dummy import Pool as ThreadPool

from Gamelog import Gamelog

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

p = ThreadPool(16)

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

        logger.debug("Home teamID: " + str(self.homeTeamID))
        logger.debug("Away teamID: " + str(self.awayTeamID))

        # Try to get an ID
        self.get_player_logs()
        result = self.get_api_id()
        if result != None:
            self.id = result
        # Try to get a home team ID
        tempHomeID = get_team_id(self.homeTeamID)
        if tempHomeID != None:
            self.homeTeamID = tempHomeID
        else:
            logger.error("Could not get home team id: " + str(self.homeTeamID))
        # Try to get away team ID
        tempAwayID = get_team_id(self.awayTeamID)
        if tempAwayID != None:
            self.awayTeamID = tempAwayID
        else:
            logger.error("Could not get away team id: " + str(self.awayTeamID))
        logger.info("HomeID: " + str(self.homeTeamID))
        logger.info("AwayID: " + str(self.awayTeamID))

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
        logger.debug(r)

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.66 Safari/537.36',
            'Connection':'keep-alive'
        }
        r = requests.get('https://therender-nba-api.herokuapp.com/game/exists/nbaid/' + self.gameID, headers=headers)
        r = r.json()
        if r["exists"] == False:
            return None
        else:
            return r["id"]

    def get_player_logs(self):
        logger.info("Getting player logs: " + str(self.gameID))
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.66 Safari/537.36',
                'Connection':'keep-alive'
            }
            r = requests.get('http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/scores/gamedetail/' + self.gameID + '_gamedetail.json', headers=headers)
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
            allData = homeData + visitingData
            p.map(self.create_game, allData)
        except ValueError, e:
            logger.error("JSON came back empty")
            logger.error(e)
            logger.error(str(self.gameID))

    def create_game(self, player):
        tempID = get_player_id(player["pid"])
        logger.debug(tempID)
        if tempID != None:
            playerID = tempID
        else:
            logger.error("No playerID")
            return
        playerID = get_player_id(player["pid"])
        logger.info("Creating gamelog for: " + str(playerID))
        gameID = self.gameID
        minutes = str(player["min"]) + ":" + str(player["sec"])
        points = player["pts"]
        rebounds = player["reb"]
        assists = player["ast"]
        steals = player["stl"]
        blocks = player["blk"]
        fieldGoalsMade = int(player["fgm"])
        fieldGoalsAttempted = int(player["fga"])
        if fieldGoalsMade is 0 or fieldGoalsAttempted is 0:
            fieldGoalPercentage = 0
        else:
            fieldGoalPercentage = fieldGoalsMade / fieldGoalsAttempted
        threePointsMade = int(player["tpm"])
        threePointsAttempted = int(player["tpa"])
        if threePointsMade is 0 or threePointsAttempted is 0:
            threePointsPercentage = 0
        else:
            threePointsPercentage = threePointsMade / threePointsAttempted
        freeThrowsMade = int(player["ftm"])
        freeThrowsAttempted = int(player["fta"])
        if freeThrowsMade is 0 or freeThrowsAttempted is 0:
            freeThrowsPercentage = 0
        else:
            freeThrowsPercentage = freeThrowsMade / freeThrowsAttempted
        fouls = int(player["pf"])
        plusMinus = int(player["pm"])

        log = Gamelog(playerID, gameID, minutes, points, rebounds, assists, steals, blocks, fieldGoalsMade, fieldGoalsAttempted, fieldGoalPercentage, threePointsMade, threePointsAttempted, threePointsPercentage, freeThrowsMade, freeThrowsAttempted, freeThrowsPercentage, fouls, plusMinus)

        log.upload()




# @type :: FUNC
# @name :: get_player_id
# @param :: nbaID - the player nbaid to look up
# @description :: Check and return the player's db id
# @return :: None or string id
# @end
def get_player_id(nbaID):
    # TODO :: ERROR HERE.  Make a try then just loop until we get a result
    logger.info("Getting player ID: " + str(nbaID))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.66 Safari/537.36',
        'Connection':'keep-alive'
    }
    try:
        r = requests.get('https://therender-nba-api.herokuapp.com/player/exists/nbaID/' + str(nbaID), headers=headers)
        r = r.json()
        if r["exists"] is True:
            return r["id"]
        else:
            return None
    except ConnectionError, e:
        logging.error("Connection Error")
        logging.error(e)
        logging.error("Retrying")
        return get_player_id(nbaID)


# @type :: FUNC
# @name :: get_team_id
# @param :: nbaID - the team nbaid to look up
# @description :: Check and return the team's db id
# @return :: None or string id
# @end
def get_team_id(nbaID):
    logger.info("Getting team ID: " + str(nbaID))
    r = requests.get('https://therender-nba-api.herokuapp.com/team/exists/nbaID/' + str(nbaID))
    r = r.json()
    if r["exists"] is True:
        logging.info("Team exists")
        return r["id"]
    else:
        logger.error("TEAM ID does not exist: " + str(nbaID))
        return None
