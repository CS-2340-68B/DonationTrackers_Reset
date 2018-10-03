from flask import Flask, render_template, redirect, session, request, url_for, flash

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/form", methods=["POST"])
def resetPass():
	return


# Run server
app.run(debug=True,host='0.0.0.0', port=5000)