from flask import Flask, render_template, redirect, session, request, g, url_for, flash, make_response, jsonify
from Server.Models.User import User
import os, time, json
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
	# print(getDonations());
	try:
		print (g.user)
	except:
		g.user = None

	if 'user' in session:
		g.user = session['user']
	print(session)

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
	return render_template("index.html", locationList=json.loads(getLocations().data))

@app.route("/getLocations")
def getLocations():
	localDB = db.child("locations")
	locations = []
	for location in localDB.get().each():
		locations.append(location.val())
	return make_response(jsonify(locations))

@app.route("/getDonations/<string:locationName>", methods=["POST", "GET"])
def getDonations(locationName):
	if request.method == "POST":
		localDB = db.child("donations").order_by_child("location").equal_to(locationName)
		donations = []
		for donation in localDB.get().each():
			d = donation.val()
			d["donationKey"] = donation.key()
			donations.append(d)
		return make_response(jsonify(donations))


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
	return render_template("home.html", username=username)

@app.route("/form", methods=["POST"])
def resetPass():
	return

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
	return  redirect(url_for('index'))


@app.route("/map", methods=["GET"])
def mapView():
	if g.user:
		if 'user' in session:
			username = session['user']
			return render_template("map.html", username=username)
	return redirect(url_for('index'))

@app.route("/test", methods=["GET"])
def testView():
	return render_template("test.html")

@app.route("/locationlist")
def locationListView():
	if g.user:
		if 'user' in session:
			username = session['user']
			return render_template("locationlist.html", username=username, locationList=json.loads(getLocations().data))
	return redirect(url_for('index'))


# @app.route("/donationdetail/<string:location>")
# def locationDetail(location):
# 	if g.user:
# 		if 'user' in session:
# 			username = session['user'] ; hashDict = {}
# 			# print(location)
# 			# for data in json.loads(getLocations().data):
# 			# 	if data['locationName'] == location:
# 			# 		hashDict = data

# 			return render_template("locationdetail.html", username=username, locationName=location)
# 	return redirect(url_for('index'))


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
				return make_response(jsonify({
					"status": "success",
					"data": account.val()
				}))
				# return redirect(url_for('home')) // Must return Json object
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
