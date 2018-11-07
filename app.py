from flask import Flask, render_template, redirect, session, request, url_for, flash, make_response, jsonify
from Server.Models.User import User
import os, time, json
import pyrebase

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
	return render_template("index.html")

@app.route("/test", methods =["POST"])
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

@app.route("/register", methods=["POST"])
def register():
	username = request.form.get("username")
	password = request.form.get("password")
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

# Sign in
@app.route("/signin", methods=["POST"])
def signin():
	checkValidUser = True
	if request.method == 'POST':
		theEmail = request.form['email_signin']
		thePassword = request.form['email_signin']
		return render_template("index.html")
	else:
		print(firebase.get('/accounts', None))
		return render_template("index.html")

# Run server
app.run(debug=True,host='0.0.0.0', port=5000)