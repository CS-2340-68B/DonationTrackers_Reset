import pyrebase, json

'''
Firebase class
'''
class Firebase():
	firebase = None
	def __init__(self):
		with open('./firebase/config.json') as json_data:
			config = json.load(json_data)
		DBfirebase = pyrebase.initialize_app(config)
		self.firebase = DBfirebase.database()

	def getAccounts_Firebase(self):
		return self.firebase.child('accounts').get().val()

	def updateAccount_Firebases(self, fixedData):
		pass

	def addNewAccount_Firebase(self, newAccount):
		pass

	def getLocation_Firebase(self):
		return self.firebase.child('locations').get().val()

	def getDonations_Firebase(self):
		return self.firebase.child('donations').get().val()