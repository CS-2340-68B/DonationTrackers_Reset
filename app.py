from flask import Flask, render_template, redirect, session, request, g, url_for, flash, make_response, jsonify
from Server.Models.User import User
from Server.Models.ItemDetail import ItemDetail
import os, time, json, requests, string
from Server.Functions.PasswordModifier import encrypt
import pyrebase
import httplib2
from threading import Timer
from functools import wraps

config = {
	"apiKey": "AIzaSyD6lGd-euEvFPpMZPNAURNRqA7pnNe-CZQ",
	"authDomain": "donationtracker-4bab8.firebaseapp.com",
	"databaseURL": "https://donationtracker-4bab8.firebaseio.com",
	"projectId": "donationtracker-4bab8",
	"storageBucket": "donationtracker-4bab8.appspot.com",
	"messagingSenderId": "554121755743"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.before_request
def before_request():
	try:
		print (g.user)
	except:
		g.user = None

	if 'user' in session:
		g.user = session['user']

def auth_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if auth and auth.username == '' and auth.password == '':
			return f(*args, **kwargs)
		return make_response('Could not verify your login', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
	return decorated

# Main page index.html
@app.route("/")
def index():
	# print(requests.get('http://localhost:5000/getDonations/'))
	return render_template("index.html", locationList=json.loads(getLocations().data))

@app.route("/getLocations")
def getLocations():
	localDB = db.child("locations")
	locations = []
	for location in localDB.get().each():
		locations.append(location.val())
	return make_response(jsonify(locations))

@app.route("/getDonations/<string:locationName>", methods=["GET", "POST"])
def getDonations(locationName):
	# if request.method == "POST":
	if not locationName:
		localDB = db.child("donations").order_by_child("location")
	else:
		localDB = db.child("donations").order_by_child("location").equal_to(locationName)
	donations = []
	for donation in localDB.get().each():
		d = donation.val()
		d["donationKey"] = donation.key()
		donations.append(d)
	return make_response(jsonify(donations))


@app.route("/getDonationsData/<string:locationName>",  methods=["GET"])
def getDonationList(locationName):
	urlPath = 'http://localhost:5000/getDonations/' + locationName
	respone = requests.get(url=urlPath) ; condition = True
	if 'type' in session:
		type = session['type']
		if type in ["ADMIN", "USER"]:
			condition = False
	return render_template("donationlist.html", donationLists=respone.json(), locationName=locationName, userType=condition)


@app.route("/getDonationItemDetail/<string:locationName>/<string:itemKey>", methods=["GET"])
def getDonationItemDetail(locationName, itemKey):
	urlPath = 'http://localhost:5000/getDonations/' + locationName
	respone = requests.get(url=urlPath).json() ; hashDict = {}
	for item in respone:
		if item['donationKey'] == itemKey:
			hashDict = item
	if g.user:
		if 'user' in session:
			username = session['user']
			return render_template("donationdetail.html", username=username, donationDetail=hashDict)
	return redirect(url_for('index'))


@app.route("/register", methods=["POST"])
def register():
	username = request.form.get("username")
	password = encrypt(request.form.get("password"))
	userType = request.form.get("userType")
	locationName = request.form.get("locationName")
	localDB = db.child("accounts").order_by_child("username").equal_to(username)
	for account in localDB.get().each():
		return make_response(jsonify({"status": "fail"}))
	user = User(username, password, userType, locationName)
	if userType == "ADMIN" or userType == "USER":
		user.assignedLocation = None
	db.child("accounts").push(user.__dict__)
	# return make_response(jsonify({"status": "Success"}))
	return render_template("home.html", username=username)

@app.route("/addItem", methods=["POST"])
def addItem():
	if g.user:
		if 'user' in session:
			username = session['user']
			category = request.form.get("categoryBox") ; name = request.form.get("nameBox")
			shortDes = request.form.get("shortBox") ; location = request.form.get("locationBox")
			fullDes = request.form.get("fullBox") ; comment = request.form.get("commentBox")
			time = request.form.get("timeBox") ; value = request.form.get("valueBox")
			item = ItemDetail(category, name, shortDes, fullDes, comment, location, time, value)
			db.child("donations").push(item.__dict__)
			# return make_response(jsonify({"status": "Success"}))
			return render_template("home.html", username=username, edit=False)

# @app.route("/editItem/<string:location>/<string:itemID>", defaults={'location' : None, 'itemID': None}, methods=["POST"])
@app.route("/editItem/<string:location>/<string:itemID>", methods=["POST", "GET"])
def editItem(location, itemID):
	if g.user:
		if 'user' in session:
			username = session['user']
			if request.method == "POST":
				category = request.form.get("categoryBox") ; name = request.form.get("nameBox")
				shortDes = request.form.get("shortBox") ; location = request.form.get("locationBox")
				fullDes = request.form.get("fullBox") ; comment = request.form.get("commentBox")
				time = request.form.get("timeBox") ; value = request.form.get("valueBox")
				donationId = request.form.get("donationID")
				item = ItemDetail(category, name, shortDes, fullDes, comment, location, time, value)
				db.child("donations").child(donationId).update(item.__dict__)
				# return make_response(jsonify({"status": "Success"}))
				return render_template("home.html")
			else:
				# Fix html convert format of and percentage
				if '&' in location:
					location = location.replace("amp;", "")

				urlPath = 'http://localhost:5000/getDonations/' + location
				respone = requests.get(url=urlPath).json() ; hashDict = {}
				for item in respone:
					if item['donationKey'] == itemID:
						hashDict = item
				return render_template("addDonation.html", edit=True, locationName=location, detail=hashDict)

@app.route("/home", methods=["GET"])
def home():
	if g.user:
		if 'user' in session:
			username = session['user']
		return render_template('home.html', username=username)
	return redirect(url_for('index'))

@app.route("/logout")
def logout():
	session.pop('user', None)
	session.pop('type', None)
	return redirect(url_for('index'))

@app.route("/map", methods=["GET"])
def mapView():
	if g.user:
		if 'user' in session:
			username = session['user']
			return render_template("dashBoard.html", username=username)
	return redirect(url_for('index'))

@app.route("/locationlist")
def locationListView():
	if g.user:
		if 'user' in session:
			username, type = session['user'], session['type']
			print(type)
			condition = True
			hashDict = json.loads(getLocations().data)
			for index in range(len(hashDict)):
				hashDict[index]['picture'] = "../static/pictures/thiftstore" + str(index) + ".png"
			if type in ["ADMIN", "USER"]:
				condition = False
			return render_template("locationlist.html", username=username, locationList=hashDict, userType=condition)
	return redirect(url_for('index'))


@app.route("/searchView", methods=["POST", "GET"])
def searchView():
	if g.user:
		if 'user' in session:
			username = session['user']
			locationList = json.loads(getLocations().data)
			# locationList.insert(0, {"locationName" : 'ALL'})
			foundData = False
			if request.method == 'POST':
				searchText = request.form['searchID']
				categorySelected = itemSelected = False
				locationName = request.form['locationName']

				# Determine if category box selected
				try:
					categorySelected = request.form['categoryChecked']
					categorySelected = True
				except:
					print("Category not selected")

				# Determine if item box selected
				try:
					itemSelected = request.form['itemChecked']
					itemSelected = True
				except:
					print("Item not selected")
				urlPath = 'http://localhost:5000/getDonations/' + locationName
				respone = requests.get(url=urlPath).json() ; result = []
				if locationName == 'ALL':
					# TODO Implement search for all locations
					pass
				else:
					if respone:
						for item in respone:
							if categorySelected:
								foundData = True
								if searchText.lower() in item['category'].lower():
									result.append(item)
							elif itemSelected:
								foundData = True
								if searchText.lower() in item['name'].lower():
									result.append(item)
						# print(result)
						return render_template(
							"search.html",
							username=username,
							locationList=locationList,
							queryOut=result,
							found=foundData
						)
			return render_template("search.html", username=username, locationList=locationList, found=foundData)
	return redirect(url_for('index'))

@app.route("/history")
def historyView():
	pass

@app.route("/addDonation/<string:location>", methods=["GET"])
def addDonation(location):
	return render_template("addDonation.html", locationName=location)

@app.route("/locationdetail/<string:location>")
def locationDetail(location):
	if g.user:
		if 'user' in session:
			username = session['user'] ; hashDict = {}
			print(location)
			for data in json.loads(getLocations().data):
				if data['locationName'] == location:
					hashDict = data
			return render_template("locationdetail.html", username=username, locationName=location, detail=hashDict)
	return redirect(url_for('index'))

# Sign in
@app.route("/signin", methods=["POST"])
def signin():
	checkValidUser = True
	if request.method == 'POST':
		session.pop('user', None) # Add new session for the user
		session.pop('type', None)
		username = request.form['email_signin']
		password = request.form['password_signin']
		localDB = db.child("accounts").order_by_child("username").equal_to(username)
		for account in localDB.get().each():
			if account.val()["isLock"]:
				return make_response(jsonify({
					"status": "accountLock",
					"data": account.val()
				}))
				# TODO
				# Return back message to current page to "Your account has been locked"
			if account.val()["password"] == encrypt(password):
				account.val()["userKey"] = account.key()
				account.val()["failedAttempts"] = 0
				db.child("accounts").child(account.key()).update(account.val())
				session['user'] = username
				session['type'] = account.val()['type']
				# return make_response(jsonify({
				# 	"status": "success",
				# 	"data": account.val()
				# }))
				return redirect(url_for('home')) # Must return Json object
			else:
				if account.val()["failedAttempts"] >= 3:
					account.val()["isLock"] = True
				else:
					account.val()["failedAttempts"] += 1
				db.child("accounts").child(account.key()).update(account.val())
				return make_response(jsonify({
					"status": "wrongPassword"
				}))
		return make_response(jsonify({
			"status": "noAccount"
		}))

def sendRequest():
	httplib2.Http().request("https://donation-tracker-server-heroku.herokuapp.com/ping")

@app.route("/ping")
def ping():
	print("PING PING PING")
	Timer(900.0, sendRequest).start()
	return make_response(jsonify({}))

# Run server
if __name__ == "__main__":
	Timer(1.0, sendRequest).start()
	app.run(debug=True,host='0.0.0.0', port=5000)
	target.parentElement.innerText