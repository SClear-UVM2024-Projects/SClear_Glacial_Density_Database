import sqlite3
from flask import Flask, render_template, request, url_for, redirect
import numpy as np
import pandas as pd
import json
import plotly
import fileinput
from plotly import data
import plotly.express as px
from os.path import exists
import string

# Final Project: Climate Change Measured by Glacial Density and Rising Sea Level
# Database Loading and Cleaning Page

# Purpose of Page: Present User with Flask Uer Interface for Title Page at least...?

# Conn is the current database file in SQL that will be edited by changes, while "cur" is the current changes that are being made!
conn = sqlite3.connect('climateChangeDatabase.db')
cur = conn.cursor()

app = Flask(__name__)

var = np.polynomial

validUser = 0

userInfoLevel = 0

validUserInformation = cur.execute("SELECT USERNAME, PASSWORD FROM users").fetchall()

locationFilenames = [["Canada", "glacialElevationCanada.csv", "averageTemperatureCanada.csv", "seaLevelCanada.csv"],
                     ["Chile", "glacialElevationChile.csv", "averageTemperatureChile.csv", "seaLevelChile.csv"],
                     ["Greenland", "glacialElevationGreenland.csv", "averageTemperatureGreenland.csv", "seaLevelGreenland.csv"],
                     ["Iceland", "glacialElevationIceland.csv", "averageTemperatureIceland.csv", "seaLevelIceland.csv"],
                     ["Pakistan", "glacialElevationPakistan.csv", "averageTemperaturePakistan.csv", "seaLevelPakistan.csv"],
                     ["United States of America", "glacialElevationUnitedStates.csv", "averageTemperatureUnitedStatesOfAmerica.csv", "seaLevelUnitedStatesOfAmerica.csv"]]

# TODO: Edge case for same username and password not returning the error message, lower priority!
# TODO: Fix Background image for the Login Screen of the Website (Flask issue)
# TODO: Immediately change the HTML link for the title page to 127.0.0.1/home_page V

@app.route('/', methods=['GET', 'POST'])
def climateChangeUserInterfaceLogin():

    validUser = 0

    username = request.form.get("username", string)
    password = request.form.get("password", string)

    for userData in validUserInformation:
        if userData[0] == username and userData[1] == password:
            validUser = 1

    # Check if the user is the admin, and if so set their "userInfoLevel" to 1.
    if username == "adminRocks031" and password == "4dm1n71m3!":
        userInfoLevel = 1
        print("here")

    # Previous login is 0 WHEN the user has logged in before
    # ValidUser is 1 when the user has entered in the correct password, and is 0 when they have not

    if username == password:
        return render_template("login.html", validUser = 1)
    elif validUser == 0:
        return render_template("login.html", validUser = 0)
    elif validUser == 1:
        return redirect('/home_page')

# TODO: Fix Variables being accepted for
# TODO: Create a hope page for petitions for new countries to add to the registry that specifically petitions from a given user on the homepage front!
# TODO: Create an interface for the graphing segment, possibly make it another drop-down from the off of the home page
# TODO: Create a pointer variable that allows the website to determine when the user is the admin, then create a drop-down that allows for the admin to add, remove, and replace specific information in the registry
# TODO: Make the Home Page look nice by formatting the page (CSS when necessary, HTML as much as I can)!

@app.route('/home_page', methods=['GET', 'POST'])
def climateChangeUserInterfaceHomePage():

    locationOne = request.form.get("locationOne", string)
    locationTwo = request.form.get("locationTwo", string)
    variableOne = request.form.get("variableOne", string)
    variableTwo = request.form.get("variableTwo", string)
    yearStart = request.form.get("yearStart", int)
    yearEnd = request.form.get("yearEnd", int)

    nullValueInt = request.form.get("nullValueInt", int)
    nullValueString = request.form.get("nullValueString", string)

    print(locationOne)
    print(locationTwo)
    print(variableOne)
    print(variableTwo)
    print(yearStart)
    print(yearEnd)
    print(userInfoLevel)


"""
    if request.method == 'POST':

        # Return an error message on the site if the user entered an invalid year
        if yearStart < 1950 or yearEnd > 2021:
            return render_template("title.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 1)
        
        # If neither variableOne or locationOne are null values, then we can create a valid graph or series of graphs.
        if variableOne != nullValueString and locationOne != nullValueString:
            if variableTwo != locationTwo:
                if variableTwo == nullValueString:
                    # One-Variable Two-Location Comparison

                    ## Location One

                    # TODO: Create a list of CSV filenames that are selected based on the credentials given by the program, create a chart based on the variables given
                    df = pd.read_csv("bech.csv")
                    df_given_year = df[df["year"] >= form_int]
                    fig = px.scatter(df_given_year, x="Btest", y="year", text="title.y")
                    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    return render_template("login.html", authorized=0)

                elif locationTwo == nullValueString:
                    # Two-Variable One-location Comparison
                else:
                    # Two-Variable Two-Location Comparison
            else:
                # One-Variable One-Location Description
        else:
            return render_template("title.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 0)
    """
    if request.method == 'GET':
        return render_template("title.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 0)
    # TODO: Create an input-output section of the site which allows any user to edit the different databases in the program, then restrict the use of this program to admin-authorization after we figure out how to do that.
    elif request.method ==
