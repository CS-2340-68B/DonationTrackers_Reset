import json

class User:
    def __init__(self, username, password, userType, locationName):
        self.username = username
        self.password = password
        self.type = userType
        self.assignedLocation = locationName
        self.failedAttempts = 0
        self.isLock = False
        self.userKey = None
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)