from flask import Flask, render_template, redirect, session, request, url_for, flash, abort
import os, time, json
import DBconnection as db

app = Flask(__name__)

# API Call use for firebase
# https://github.com/thisbejim/Pyrebase

# Connecting to Firebase
connect = db.Firebase()
donationList = connect.getDonations_Firebase()
# print(donationList)

# Main page index.html
@app.route("/")
def index():
	return render_template("index.html")

# Sign in
@app.route("/signin", methods=["POST"])
def signin():
	checkValidUser = True
	if request.method == 'POST':
		theEmail = request.form['email_signin']
		thePassword = request.form['password_signin']
		return render_template("index.html")
	else:
		print(firebase.get('/accounts', None))
		return render_template("index.html")

# Run server
app.run(debug=True,host='0.0.0.0', port=5000)