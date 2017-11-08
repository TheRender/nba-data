# @type :: CLASS
# @class :: Team
# @author :: Steven Hanna
# @description :: Class to contain team management
# @end

import json
import requests
import logging
from multiprocessing.dummy import Pool as ThreadPool

from Player import Player

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

season = "2017-18"

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
    # @param :: games - an array of games id's in association with our API
    # @end
    def __init__(self, name, city, tricode, teamID, players, logo, nickname, seasonWins, seasonLosses, location, games):
        # self.id = apiID
        logger.info("Creating team object: " + name)
        self.name = name
        self.city = city
        self.tricode = tricode
        self.players = []
        self.logo = logo
        self.teamID = teamID
        self.seasonWins = seasonWins
        self.seasonLosses = seasonLosses
        self.location = location
        self.games = games
        self.nickname = nickname
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
        logger.info("Uploading new: " + self.name)
        r = requests.post('https://therender-nba-api.herokuapp.com/team/new', data=self.json_dump())

    # @type :: FUNC
    # @name :: upload_existing
    # @param :: self - self representation
    # @description :: Uploads an existing team as an edit
    # @end
    def upload_existing(self):
        logger.info("Uploading existing: " + self.name)
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
        logger.info("Getting players: " + self.name + ", " + str(self.teamID))
        logger.info('http://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=" + season + "&TeamID=' + str(self.teamID))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.66 Safari/537.36',
            'Connection':'keep-alive'
        }
        try:
            r = requests.get('http://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=" + season + "&TeamID=' + str(self.teamID), headers=headers, timeout=3)
            r = r.json()
            logger.info("NBA API request complete")
            rowSet = r["resultSets"][0]["rowSet"]
            playerObjects = []
            for x in rowSet:
                headshotURL = "http://stats.nba.com/media/players/230x185/" + str(x[12]) + ".png"
                playerObjects.append((Player(x[12], x[3], headshotURL, self.name, self.id, x[4], x[5], 0, 0, 0, [])))
                # y.upload()

            # Use a pool to map over the playerObjects
            p = ThreadPool(16)
            p.map(self.parallel_upload, playerObjects)
            p.close()
            p.join()
            return
        except requests.exceptions.Timeout, e:
            logging.error("Timeout")
            logging.error(e)
            logging.error("Try again")
            self.get_players()

    def parallel_upload(self, player):
        print("Uploading player: " + player.name)
        player.upload()
        self.players.append(player.id)
