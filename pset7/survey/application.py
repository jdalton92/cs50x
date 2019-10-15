import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    fullname = request.form.get("full-name")
    email = request.form.get("email-address")
    gender = request.form.get("gender-radios")
    language = request.form.get("favourite-language")
    if not fullname or not email or not gender or not language:
        return render_template("error.html", message="Please complete name, email, gender and favourite language fields")
    file = open("survey.csv", "a")
    writer = csv.writer(file)
    writer.writerow((fullname, email, gender, language))
    file.close()
    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    file = open("survey.csv", "r")
    reader = csv.reader(file)
    registered = list(reader)
    return render_template("sheet.html", registered=registered)
