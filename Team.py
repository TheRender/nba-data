# @type :: CLASS
# @class :: Team
# @author :: Steven Hanna
# @description :: Class to contain team management
# @end

import json

class Team(object):

    def __init__(self, apiID, name, city, teamID, players, logo, seasonWins, seasonLosses, location, logs):
        self.apiID = apiID
        self.name = name
        self.city = city
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


x = Team("123", "Test", "Test", "Test", "Test", "Test", "Test", "Test", "Test", ["Test"])
x.upload()
