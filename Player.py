# @type :: CLASS
# @class :: Player
# @author :: Steven Hanna
# @description :: Class to contain player management
# @end

import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    def __init__(self, playerID, name, headshotURL, teamName, teamID, jerseyNumber, position, careerPPG, careerRPG, careerAPG, stats):
        logger.info("Creating player object: " + name)
        self.name = name
        self.playerID = playerID
        self.headshotURL = headshotURL
        self.teamName = teamName
        self.teamID = teamID
        self.jerseyNumber = jerseyNumber
        self.position = position
        self.careerPPG = careerPPG
        self.careerRPG = careerRPG
        self.careerAPG = careerAPG
        self.stats = []
        self.gamelogs = []
        self.get_career_stats()
        # Try to get an ID
        result = self.get_api_id()
        if result != None:
            self.id = result


    # @type :: FUNC
    # @name :: upload
    # @param :: self - self representation
    # @description :: Determines and executes whether to upload with our without api id
    def upload(self):
        logger.info("Uploading: " + self.name)
        if hasattr(self, "id"):
            self.upload_existing()
        else:
            # Attempt to get an id
            val = self.get_api_id()
            print(val)
            if val is None:
                self.id = self.upload_new()
            else:
                self.upload_existing()

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
        logger.info("Uploading new: " + self.name + ", " + str(self.playerID))
        r = requests.post('https://therender-nba-api.herokuapp.com/player/new', data=self.json_dump())
        try:
            r = r.json()
            return r["player"]["id"]
        except ValueError:
            logger.error("Error extracting the JSON.")
            logger.error("No JSON was sent.")
            logger.error(r)

    # @type :: FUNC
    # @name :: upload_existing
    # @param :: self - self representation
    # @description :: Uploads an existing player as an edit
    # @end
    def upload_existing(self):
        logger.info("Uploading existing: " + self.name + ", " + str(self.playerID))
        r = requests.post('https://therender-nba-api.herokuapp.com/player/edit', data=self.json_dump())

    # @type :: FUNC
    # @name :: get_api_id
    # @param :: self
    # @returns :: False | the referenced API ID
    # @description :: Determines if the player exists or not. If it does, it
    # supplies the API id
    # @end
    def get_api_id(self):
        r = requests.get('https://therender-nba-api.herokuapp.com/player/exists/nbaid/' + str(self.playerID))
        try:
            r = r.json()
        except ValueError:
            logger.error("Error extracting the JSON.")
            logger.error("No JSON was sent.")
            logger.error(r)
        if r["exists"] == False:
            return None
        else:
            return r["id"]


    def get_career_stats(self):
        logger.info("Getting career stats: " + self.name)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.66 Safari/537.36',
            'Connection':'keep-alive'
        }
        logging.debug("http://stats.nba.com/stats/playercareerstats?LeagueID=00&PerMode=PerGame&PlayerID=" + str(self.playerID))
        try:
            r = requests.get('http://stats.nba.com/stats/playercareerstats?LeagueID=00&PerMode=PerGame&PlayerID=' + str(self.playerID), headers=headers, timeout=2)
            logging.debug(r)
            r = r.json()
            results = r["resultSets"][1]["rowSet"][0]
            self.careerPPG = results[23]
            self.careerRPG = results[17]
            self.careerAPG = results[18]
            return
        except requests.exceptions.Timeout, e:
            logging.error("Timeout")
            logging.error(e)
            logging.error("Trying again")
            self.get_career_stats()
        except ValueError:
            logger.error("Error extracting the JSON")
            logger.error(r)
        except IndexError:
            logger.error("The NBA is being stupid and messed up their API")
            logger.error("Index error out of bounds somewhere")
        except ConnectionError:
            logging.error("Connection Error")
            logging.error(e)
            logging.error("Trying again")
            self.get_career_stats()
