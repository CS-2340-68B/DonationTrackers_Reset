from flask import Flask, render_template, redirect, session, request, url_for, flash, make_response, jsonify
from Server.Models.User import User
import os, time, json
from Server.Functions.PasswordModifier import encrypt
import pyrebase
import httplib2
from threading import Timer

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

# Main page index.html
@app.route("/")
def index():
	return render_template("index.html", locationList=json.loads(getLocations().data))

@app.route("/test", methods =["POST", "GET"])
def test():
	# body = request.form
	# # username = body["criteria"]
	# user = body.get("criteria[failedAttempts]")
	# print(user)
	# print(body)
	# # print(username)
	# # accounts = db.child("accounts").get()
	# # print(accounts)
	# # print("123")
	# return make_response(jsonify({"Tuan": "Nguyen"}))
	body = request.json
	item = {
		"username": "tuannguyen",
		"password": "123456"
	}
	return make_response(jsonify(item))

@app.route("/getLocations")
def getLocations():
	localDB = db.child("locations")
	locations = []
	for location in localDB.get().each():
		locations.append(location.val())
	return make_response(jsonify(locations))

@app.route("/getDonations", methods=["POST", "GET"])
def getDonations():
	if request.method == "POST":
		locationName = request.form.get("locationName")
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
	return make_response(jsonify({"status": "success"}))

@app.route("/form", methods=["POST"])
def resetPass():
	return

@app.route("/home", methods=["GET"])
def home():
	return render_template("home.html")

# Sign in
@app.route("/signin", methods=["POST"])
def signin():
	checkValidUser = True
	if request.method == 'POST':
		username = request.form['email_signin']
		password = request.form['password_signin']
		localDB = db.child("accounts").order_by_child("username").equal_to(username)
		for account in localDB.get().each():
			if account.val()["isLock"]:
				return make_response(jsonify({
					"status": "accountLock",
					"data": account.val()
				}))
			if account.val()["password"] == encrypt(password):
				account.val()["userKey"] = account.key()
				account.val()["failedAttempts"] = 0
				db.child("accounts").child(account.key()).update(account.val())
				# return make_response(jsonify({
				# 	"status": "success",
				# 	"data": account.val()
				# }))
				return render_template("home.html")
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
	# else:
	# 	return render_template("index.html")

def sendRequest():
	httplib2.Http().request("https://donation-tracker-server-heroku.herokuapp.com/ping")
	# httplib2.Http().request("http://localhost:5000/ping")

@app.route("/ping")
def ping():
	print("PING PING PING")
	Timer(60.0, sendRequest).start()
	return make_response(jsonify({}))

# Run server
if __name__ == "__main__":
	Timer(1.0, sendRequest).start()
	app.run(debug=True,host='0.0.0.0', port=5000)