import sqlite3
from typing import Dict

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
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Final Project: Climate Change Measured by Glacial Density and Rising Sea Level
# Database Loading and Cleaning Page

# Purpose of Page: Present User with Flask Uer Interface for Title Page at least...?

# Conn is the current database file in SQL that will be edited by changes, while "cur" is the current changes that are being made!
conn = sqlite3.connect('climateChangeDatabase.db', check_same_thread=False)
cur = conn.cursor()
app = Flask(__name__)
var = np.polynomial

# Initializing user info for first connection to site
validUser = 0
_USER_INFO_LEVEL = {"User": 0, "Name": "Unknown"}
validUserInformation = cur.execute("SELECT Username, Password, User_Access, Display_Name FROM USERS").fetchall()

# Dictionary for database titling info
locationTableNames = [["Canada", "GLACIALELEVATIONCANADA", "TEMPERATURESCANADA", "SEALEVELCANADA"],
                     ["Chile", "GLACIALELEVATIONCHILE", "TEMPERATURESCHILE", "SEALEVELCHILE"],
                     ["Greenland", "GLACIALELEVATIONGREELAND", "TEMPERATURESGREENLAND", "SEALEVELGREENLAND"],
                     ["Iceland", "GLACIALELEVATIONICELAND", "TEMPERATURESICELAND", "SEALEVELICELAND"],
                     ["Pakistan", "GLACIALELEVATIONPAKISTAN", "TEMPERATURESPAKISTAN", "SEALEVELPAKISTAN"],
                     ["United States of America", "GLACIALELEVATIONUNITEDSTATESOFAMERICA", "TEMPERATURESUNITEDSTATESOFAMERICA", "SEALEVELUNITEDSTATESOFAMERICA"]]
locationNamesAllCaps = {"Canada": "CANADA", "Chile": "CHILE", "Greenland": "GREENLAND", "Iceland": "ICELAND", "Pakistan": "PAKISTAN", "United States of America": "UNITEDSTATESOFAMERICA"}

# Auxiliary Functions for application use
# To test if the value inputted is a valid input, we must test if any type of number is a float
# or an integer. We will do this with a "try-except" block from the following source:
# https://www.programiz.com/python-programming/examples/check-string-number
def isFloat(valueIntoDatabase):
    try:
        float(valueIntoDatabase)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def isInteger(valueIntoDatabase):
    try:
        int(valueIntoDatabase)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


# Application log-in back-end
@app.route('/', methods=['GET', 'POST'])
def climateChangeUserInterfaceLogin():

    validUser = 0

    username = request.form.get("username", string)
    password = request.form.get("password", string)
    adminUsername = ""
    adminPassword = ""
    nullInputString = request.form.get("nullInput", string)

    for userData in validUserInformation:
        if userData[2] == 1 or userData[2] == "1":
            adminUsername = userData[0]
            adminPassword = userData[1]
        if userData[0] == username and userData[1] == password:
            validUser = 1
            _USER_INFO_LEVEL[1] = userData[3]

    # Check if the user is the admin, and if so set their "userInfoLevel" to 1 then
    # their access level changes to the admin access level.
    # This program is designed for only one Admin user to have access.
    if username == adminUsername and password == adminPassword:
        _USER_INFO_LEVEL[0] = 1
    else:
        _USER_INFO_LEVEL[0] = 0

    # Previous login is 0 WHEN the user has logged in before
    # ValidUser is 1 when the user has entered in the correct password, and is 0 when they have not

    if username == nullInputString or password == nullInputString:
        return render_template("login.html", invalidInput = 0)
    elif validUser == 0:
        return render_template("login.html", invalidInput = 1)
    elif validUser == 1:
        return redirect('/home_page')

# TODO: Create a home page for PETITIONS for new countries to add to the registry that specifically PETITIONS from a given user on the homepage front!
# TODO: Make the Home Page look nice by formatting the page (CSS when necessary, HTML as much as I can)!

@app.route('/petition_input', methods=['GET', 'POST'])
def climateChangeUserInterfacePetitionPage():

    name = _USER_INFO_LEVEL["Name"]
    country = request.form.get("country", string)
    reason = request.form.get("reason", string)

    nullValueString = request.form.get("nullValueString", string)
    nullValueInt = request.form.get("nullValueInt", int)

    if request.method == "GET":
        return render_template("petitionInput.html", invalidInput=0)

    if request.method == "POST":

        # Certain Character Edge Case
        if (reason.find("\'") != -1 or reason.find("\"") != -1) and (country.find("\'") != -1 or country.find("\"") != -1):
            return render_template("petitionInput.html", invalidInput = 1)

        # If the user enters no input, request the user enter in the correct input
        if country == nullValueString or country == "" or reason == nullValueString or reason == "":
            return render_template("petitionInput.html", invalidInput = 1)

        # If the user enters all of the values, then enter in all of the values as a new petition value.
        else:
            rowMax = cur.execute(f"SELECT max(PETITION_ID) FROM PETITIONS").fetchall()
            rowMax = rowMax[0][0]
            rowMax = rowMax + 1
            cur.execute(f"INSERT INTO PETITIONS (PETITION_ID, Display_Name, Country, Reason) values ({rowMax}, '{name}', '{country}', '{reason}')")
            conn.commit()
            return redirect('/home_page')

    else:
        return render_template("petitionInput.html", invalidInput = 1)


@app.route('/admin_input', methods=['GET', 'POST'])
def climateChangeUserInterfaceInputPage():

    conn = sqlite3.connect('climateChangeDatabase.db')
    cur = conn.cursor()

    # Collect each of the pieces of info from the HTML Website, including of
    # data to modify and which section of the database the data is.
    variableType = request.form.get("variableType", string)
    valueInDatabase = request.form.get("valueInDatabase", string)
    valueIntoDatabase = request.form.get("valueIntoDatabase", string)
    columnName = request.form.get("columnName", string)
    rowIndex = request.form.get("rowIndex", string)
    replacementType = request.form.get("replacementType", string)
    returnToHome = request.form.get("returnToHome", string)
    locationToEdit = request.form.get("locationToEdit", string)
    if locationToEdit in locationNamesAllCaps.keys():
        locationToEdit = locationNamesAllCaps[locationToEdit]

    # Record a null string value, in case any of the values were lost
    nullValueString = request.form.get("nullValueString", string)

    # Testing of each variable, "" means that there was a value entered by it was recieved as Null
    print(locationToEdit)
    print(variableType)
    print(valueInDatabase)
    print(valueIntoDatabase)
    print(columnName)
    print(rowIndex)
    print(replacementType)
    print(returnToHome)
    print(_USER_INFO_LEVEL[0])

    # Initially assume that the input is not invalid
    invalidInput = 0
    completedInput = 0

    # Check if the user has selected to return to the home screen, redirect if so
    if returnToHome != nullValueString:
        if returnToHome == "yes":
            return redirect('/home_page')

    # Test the different pieces of information to ensure that invalid
    # modifications are not made/attempted in the SQL Database.
    if replacementType != nullValueString:

        if locationToEdit == nullValueString or variableType == nullValueString or columnName == "NULL":
            return render_template("input.html", invalidInput = 1, completedInput = 0)

        if replacementType == "Modify" and (valueInDatabase != "NULL" or valueIntoDatabase != "NULL"):

            if variableType == "Glacial Elevation" and (columnName == "Glacial_Density" or columnName == "Year") and isInteger(rowIndex) and int(rowIndex) >= 0 and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "GLACIALELEVATION" + locationToEdit
                rowMax = cur.execute(f"SELECT max(ELEVATION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput = 1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = {valueIntoDatabase} WHERE ELEVATION_ID = {int(rowIndex)}")
                    conn.commit()
                    return render_template("input.html", invalidInput = 0, completedInput = 1)
            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth") and isInteger(rowIndex) and int(rowIndex) >= 0 and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "temperatures" + locationToEdit + "Two"
                print("Got to the Averages Section of " + tableName)
                rowMax = cur.execute(f"SELECT max(TEMPERATURE_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    print("FailRowMax")
                    return render_template("input.html", invalidInput = 1, completedInput = 0)
                else:
                    print(f"UPDATE {tableName} SET {columnName} = {valueIntoDatabase} WHERE TEMPERATURE_ID = {int(rowIndex)}")
                    cur.execute(f"UPDATE {tableName} SET {columnName} = {valueIntoDatabase} WHERE TEMPERATURE_ID = {int(rowIndex)}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)

            elif variableType == "Sea Level" and (((columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase))) or (columnName == "Month")) and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "seaLevel" + locationToEdit + "Two"
                rowMax = cur.execute(f"SELECT max(SEA_LEVEL_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput = 1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE SEA_LEVEL_ID = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput = 1)

            elif variableType == "User Data" and (columnName == "Username" or columnName == "Password" or columnName == "Display_Name" or columnName == "User_Access") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "USERS"
                rowMax = cur.execute(f"SELECT max(USER_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE USER_ID = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Petition Data" and (columnName == "Display_Name" or columnName == "Country" or columnName == "Reason") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "PETITIONS"
                rowMax = cur.execute(f"SELECT max(PETITION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE PETITION_ID = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            else:
                print("Fail VariableType")
                return render_template("input.html", invalidInput = 1, completedInput = 0)

        elif replacementType == "Remove":
            if variableType == "Glacial Elevation" and (columnName == "Glacial_Density" or columnName == "Year") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "GLACIALELEVATION" + locationToEdit
                tableNameTemp = "glacialElevationTemp"
                rowMax = cur.execute(f"SELECT max(ELEVATION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0][0]
                # If the index is invalid, then notify the user
                if rowMax < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                # If the row index is valid but no value was entered, then the entire row is removed.
                elif valueInDatabase == "NULL":
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE ELEVATION_ID != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    print("here1")
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    print(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE ELEVATION_ID == {rowIndex}")
                    cur.execute(f"UPDATE '{tableName}' SET {columnName} = NULL WHERE ELEVATION_ID == {rowIndex}")
                    conn.commit()
                    print("here2")
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "temperatures" + locationToEdit + "Two"
                tableNameTemp = "temperaturesTemp"
                rowMax = cur.execute(f"SELECT max(TEMPERATURE_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == "NULL":
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE TEMPERATURE_ID != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE TEMPERATURE_ID == '{rowIndex}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Sea Level" and ((columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") or (columnName == "Month")) and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "seaLevel" + locationToEdit + "Two"
                tableNameTemp = "seaLevelTemp"
                rowMax = cur.execute(f"SELECT max(SEA_LEVEL_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == "NULL":
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE SEA_LEVEL_ID != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE SEA_LEVEL_ID == '{rowIndex}'")
                    conn.commit()
                    return render_template("input.html", invalidInput = 0, completedInput = 1)
            elif variableType == "User Data" and (columnName == "Username" or columnName == "Password" or columnName == "Display_Name" or columnName == "User_Access") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "USERS"
                tableNameTemp = "USERSTemp"
                rowMax = cur.execute(f"SELECT max(USER_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == "NULL":
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE USER_ID != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE USER_ID == '{rowIndex}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Petition Data" and (columnName == "Display_Name" or columnName == "Country" or columnName == "Reason") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "PETITIONS"
                tableNameTemp = "PETITIONSTemp"
                rowMax = cur.execute(f"SELECT max(PETITION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == "NULL":
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE PETITION_ID != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE PETITION_ID == {rowIndex}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            else:
                return render_template("input.html", invalidInput = 1, completedInput=0)

        # Row index is used to determine if the user wishes to add a new data row, or to add data to an existing row
        elif replacementType == "Add" and (valueInDatabase != "NULL" or valueIntoDatabase != "NULL"):
            if variableType == "Glacial Elevation" and (columnName == "Glacial_Density" or columnName == "Year") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "GLACIALELEVATION" + locationToEdit
                rowMax = cur.execute(f"SELECT max(ELEVATION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0][0]
                newRowIndex = int(rowMax) + 1
                # If row is within the database, the value is added to the line of data
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE {tableName} SET {columnName} = {valueIntoDatabase} WHERE ELEVATION_ID = {int(rowIndex)}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)

                # If the row is not within the database, than a new row is created from the existing details if the existing details are correct
                elif rowIndex == "NULL":
                    print("goal 1")
                    if columnName == "Year":
                        print("goal 2")
                        cur.execute(f"INSERT INTO {tableName} (ELEVATION_ID, Year, Glacial_Density) VALUES ('{newRowIndex}', '{valueIntoDatabase}', NULL)")
                    elif columnName == "Glacial_Density":
                        cur.execute(f"INSERT INTO {tableName} (ELEVATION_ID, Year, Glacial_Density) VALUES ('{newRowIndex}', 2022, '{valueIntoDatabase}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput = 1, completedInput = 0)

            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "TEMPERATURES" + locationToEdit
                rowMax = cur.execute(f"SELECT max(TEMPERATURE_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0][0]
                newRowIndex = int(rowMax) + 1
                # If row is within the database, the value is added to the line of data
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE {tableName} SET {columnName} = {valueIntoDatabase} WHERE TEMPERATURE_ID = {int(newRowIndex)}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)

                # If the row is not within the database, than a new row is created from the existing details if the existing details are correct
                elif rowIndex == "NULL":
                    if columnName == "Annual_Mean":
                        cur.execute(f"INSERT INTO {tableName} (TEMPERATURE_ID, 'Year', 'Annual_Mean', 'Five_Year_Smooth') VALUES ('{newRowIndex}', NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "Year":
                        cur.execute(f"INSERT INTO {tableName} (TEMPERATURE_ID, 'Year', 'Annual_Mean', 'Five_Year_Smooth') VALUES ('{newRowIndex}', '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "Five_Year_Smooth":
                        cur.execute(f"INSERT INTO {tableName} (TEMPERATURE_ID, 'Year', 'Annual_Mean', 'Five_Year_Smooth') VALUES ('{newRowIndex}', NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)

            elif variableType == "Sea Level" and (((columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase))) or (columnName == "Month")):
                tableName = "seaLevel" + locationToEdit + "Two"
                rowMax = cur.execute(f"SELECT max(SEA_LEVEL_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                newRowIndex = int(rowMax[0]) + 1
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax[0] >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE SEA_LEVEL_ID = '{int(newRowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                elif rowIndex == "NULL":
                    if columnName == "Month":
                        cur.execute(f"INSERT INTO {tableName} (SEA_LEVEL_ID, 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', '{valueIntoDatabase}', NULL, NULL, NULL)")
                    elif columnName == "Year":
                        cur.execute(f"INSERT INTO {tableName} (SEA_LEVEL_ID, 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', NULL, '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "Average_Monthly_Anomaly":
                        cur.execute(f"INSERT INTO {tableName} (SEA_LEVEL_ID, 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', NULL, NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "Average_Annually_Anomaly":
                        cur.execute(f"INSERT INTO {tableName} (SEA_LEVEL_ID, 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', NULL, NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput="1", completedInput="0")
            elif variableType == "User Data" and (columnName == "Username" or columnName == "Password" or columnName == "Display_Name" or columnName == "User_Access"):
                tableName = "USERS"
                rowMax = cur.execute(f"SELECT max(PETITION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                newRowIndex = int(rowMax[0]) + 1
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE PETITION_ID = '{int(newRowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                elif rowIndex == "NULL":
                    if columnName == "Username":
                        cur.execute(f"INSERT INTO {tableName} (USER_ID, 'Username', 'Password', 'Display_Name', 'User_Access') VALUES ('{newRowIndex}', '{newRowIndex + 1}', '{valueIntoDatabase}', NULL, NULL, NULL)")
                    elif columnName == "Password":
                        cur.execute(f"INSERT INTO {tableName} (USER_ID, 'Username', 'Password', 'Display_Name', 'User_Access') VALUES ('{newRowIndex}', '{newRowIndex + 1}', NULL, '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "Display_Name":
                        cur.execute(f"INSERT INTO {tableName} (USER_ID, 'Username', 'Password', 'Display_Name', 'User_Access') VALUES ('{newRowIndex}', '{newRowIndex + 1}', NULL, NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "User_Access":
                        cur.execute(f"INSERT INTO {tableName} (USER_ID, 'Username', 'Password', 'Display_Name', 'User_Access') VALUES ('{newRowIndex}', '{newRowIndex + 1}', NULL, NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)
            elif variableType == "Petition Data" and (columnName == "Display_Name" or columnName == "Country" or columnName == "Reason"):
                tableName = "PETITIONS"
                rowMax = cur.execute(f"SELECT max(PETITION_ID) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                newRowIndex = int(rowMax[0]) + 1
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE PETITION_ID = '{int(newRowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                elif rowIndex == "NULL":
                    if columnName == "Display_Name":
                        cur.execute(f"INSERT INTO {tableName} ('PETITION_ID' 'Display_Name', 'Country', 'Reason') VALUES ('{newRowIndex}', '{newRowIndex}', '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "Country":
                        cur.execute(f"INSERT INTO {tableName} ('PETITION_ID' 'Display_Name', 'Country', 'Reason') VALUES ('{newRowIndex}', '{newRowIndex}', NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "Reason":
                        cur.execute(f"INSERT INTO {tableName} ('PETITION_ID' 'Display_Name', 'Country', 'Reason') VALUES ('{newRowIndex}', '{newRowIndex}', NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=1, completedInput=0)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)
            else:
                print("Bad End")
                return render_template("input.html", invalidInput=1, completedInput=0)

        # If the user has selected to search, then the database will show a table of the all of the data which satisfied the condition of "columnName == valueInDatabase". This will be done by
        elif replacementType == "Search" and (valueInDatabase != "NULL" or valueIntoDatabase != "NULL"):
            if variableType == "Glacial Elevation" and (columnName == "Glacial_Density" or columnName == "Year"):
                tableName = "GLACIALELEVATION" + locationToEdit
                df = pd.read_sql_query(f"SELECT * FROM {tableName} WHERE {columnName} == '{valueInDatabase}'", conn)
                df = df.sort_values(by=["ELEVATION_ID"])
                fig = go.Figure(data=[go.Table(header=dict(values=list(df.columns)), cells=dict(values=[df.ELEVATION_ID, df.Year, df.Glacial_Density]))])
                fig.update_layout(width=700, height=300)
                graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template("input.html", invalidInput=0, completedInput=1, dataRequested=graph_json,
                                       graphImported=1)

            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth"):
                tableName = "SELECT * FROM TEMPERATURES" + locationToEdit + "WHERE " + columnName + " == " + valueInDatabase
                df = pd.read_sql_query(tableName, conn)
                df = df.sort_values(by=["TEMPERATURE_ID"])
                fig = go.Figure(data=[go.Table(header=dict(values=list(df.columns)), cells=dict(values=[df.TEMPERATURE_ID, df.Year, df.Annual_Mean, df.Five_Year_Smooth]))])
                fig.update_layout(width=700, height=300)
                graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template("input.html", invalidInput=0, completedInput=1, dataRequested=graph_json,graphImported=1)

            elif variableType == "Sea Level" and (columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") or (columnName == "Month"):
                tableName = "SELECT * FROM SEALEVEL" + locationToEdit + "Two WHERE " + columnName + " == " + valueInDatabase
                df = pd.read_sql_query(tableName, conn)
                df = df.sort_values(by=["SEA_LEVEL_ID"])
                fig = go.Figure(data=[go.Table(header=dict(values=list(df.columns)), cells=dict(values=[df.SEA_LEVEL_ID, df.Month, df.Year, df.Average_Monthly_Anomaly, df.Average_Annual_Anomaly]))])
                fig.update_layout(width=700, height=300)
                graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template("input.html", invalidInput=0, completedInput=1, dataRequested=graph_json, graphImported=1)

            elif variableType == "User Data" and (columnName == "Username" or columnName == "Password" or columnName == "Display_Name" or columnName == "User_Access"):
                df = pd.read_sql_query(f"SELECT * FROM USERS WHERE {columnName} == '{valueInDatabase}'", conn)
                df = df.sort_values(by=["USER_ID"])
                fig = go.Figure(data=[go.Table(header = dict(values=list(df.columns)), cells = dict(values=[df.USER_ID, df.Username, df.Password, df.Display_Name, df.User_Access]))])
                fig.update_layout(width=700, height=300)
                graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template("input.html", invalidInput=0, completedInput=1, dataRequested = graph_json, graphImported = 1)

            elif variableType == "Petition Data" and (columnName == "Display_Name" or columnName == "Country" or columnName == "Reason"):
                df = pd.read_sql_query(f"SELECT * FROM PETITIONS WHERE {columnName} == {valueInDatabase}", conn)
                df = df.sort_values(by="PETITION_ID")
                fig = go.Figure(data=[go.Table(header=dict(values=list(df.columns)), cells=dict(values=[df.PETITION_ID, df.Display_Name, df.Country, df.Reason]))])
                fig.update_layout(width=700, height=300)
                graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template("input.html", invalidInput=0, completedInput=1, dataRequested=graph_json,graphImported=1)

            else:
                return render_template("input.html", invalidInput=1, completedInput=0)
        else:
            print("Fail ReplacementType")
            return render_template("input.html", invalidInput=0, completedInput=1)
    else:
        print("No Input Given")
        return render_template("input.html", invalidInput = 0, completedInput = 0)

@app.route('/home_page', methods=['GET', 'POST'])
def climateChangeUserInterfaceHomePage():
    variableTypeDictionary = {"Glacial Elevation": 'Glacial_Density', "Surface Temperature Average": 'Annual_Mean',
                              "Sea Level": 'Average_Annual_Anomaly'}
    locationByVariableDictionary = {
        "Glacial Elevation": {"Canada": "GLACIALELEVATIONCANADA", "Chile": "GLACIALELEVATIONCHILE",
                              "Greenland": "GLACIALELEVATIONGREENLAND", "Iceland": "GLACIALELEVATIONICELAND",
                              "Pakistan": "GLACIALELEVATIONPAKISTAN",
                              "United States of America": "GLACIALELEVATIONUNITEDSTATESOFAMERICA"},
        "Surface Temperature Average": {"Canada": "TEMPERATURESCANADA", "Chile": "TEMPERATURESCHILE",
                                        "Greenland": "TEMPERATURESGREENLAND", "Iceland": "TEMPERATURESICELAND",
                                        "Pakistan": "TEMPERATURESPAKISTAN",
                                        "United States of America": "TEMPERATURESUNITEDSTATESOFAMERICA"},
        "Sea Level": {"Canada": "SEALEVELCANADA", "Chile": "SEALEVELCHILE", "Greenland": "SEALEVELGREENLAND",
                      "Iceland": "SEALEVELICELAND", "Pakistan": "SEALEVELPAKISTAN",
                      "United States of America": "SEALEVELUNITEDSTATESOFAMERICA"}}

    locationOne = request.form.get("locationOne", string)
    locationTwo = request.form.get("locationTwo", string)
    variableOne = request.form.get("variableOne", string)
    variableTwo = request.form.get("variableTwo", string)
    yearStart = request.form.get("yearStart", int)
    yearEnd = request.form.get("yearEnd", int)
    exampleNumber = request.form.get("exampleNumber", string)
    inputType = request.form.get("inputType", string)
    statisticalMethodToAdd = request.form.get("statisticalMethodToAdd", string)
    statisticalMethodColumnName = request.form.get("statisticalMethodColumnName", string)

    nullValueInt = request.form.get("nullValueInt", int)
    nullValueString = request.form.get("nullValueString", string)

    if exampleNumber != nullValueString and exampleNumber != "":
        if exampleNumber == "example1":
            locationOne = "Canada"
            locationTwo = "None"
            variableOne = "Glacial Elevation"
            variableTwo = "None"
            yearStart = 2014
            yearEnd = 2019
            statisticalMethodToAdd = "Maximum Value"

        elif exampleNumber == "example2":
            locationOne = "Iceland"
            locationTwo = "None"
            variableOne = "Sea Level"
            variableTwo = "Surface Temperature Average"
            yearStart = 2000
            yearEnd = 2019
            statisticalMethodToAdd = "Mean Value"

        elif exampleNumber == "example3":
            locationOne = "Chile"
            locationTwo = "United States of America"
            variableOne = "Glacial Elevation"
            variableTwo = "Sea Level"
            yearStart = 2000
            yearEnd = 2020
            statisticalMethodToAdd = "Maximum Value"

    if _USER_INFO_LEVEL[0] != 0 and _USER_INFO_LEVEL[0] != 1:
        _USER_INFO_LEVEL[0] = 0

    authorizedUser = _USER_INFO_LEVEL[0]

    if request.method == "GET":
        return render_template("homePage.html", authorizedUser = _USER_INFO_LEVEL[0], invalidInput = 0)

    if request.method == 'POST':

        print(locationOne)
        print(locationTwo)
        print(variableOne)
        print(variableTwo)
        print(yearStart)
        print(yearEnd)
        print(exampleNumber)
        print(inputType)
        print(_USER_INFO_LEVEL[0])
        print(statisticalMethodColumnName)
        print(statisticalMethodToAdd)

        statisticalDataPresent = 0
        statisticalMethodData = ""

        if inputType == "petition":
            return redirect('/petition_input')

        elif inputType == "adminInput":
            return redirect('/admin_input')

        else:
            print("Here?")
            if isInteger(yearStart) and isInteger(yearEnd):
                yearStart = int(yearStart)
                yearEnd = int(yearEnd)

            # Return an error message on the site if the user entered an invalid year
            if isInteger(yearStart) and isInteger(yearEnd):
                if (int(yearStart) < 1900 or int(yearEnd) > 2022):
                    return render_template("homePage.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 1)

            # If neither variableOne or locationOne are null values, then we can create a valid graph or series of graphs.
            if variableOne != nullValueString and locationOne != nullValueString and yearStart != nullValueInt and yearEnd != nullValueInt:
                if True:
                    if variableTwo == "None" and locationTwo != "None":
                        # One-Variable Two-Location Comparison

                        print("One-Var Two-Loc Graph")
                        # Label each of the graphs by the given variable
                        graphOneTitle = variableOne + " of " + locationOne
                        graphTwoTitle = variableOne + " of " + locationTwo
                        graphThreeTitle = "Correlation of " + variableOne + " and " + variableTwo

                        # Create the figure to output to the system
                        fig = make_subplots(rows=1, cols=3, subplot_titles = [graphOneTitle, graphTwoTitle, graphThreeTitle])

                        ## Graph One

                        # If the first location is Canada, then create this particular graph
                        if locationOne == locationTableNames[0][0]:
                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    print("Kicked nonint years")
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        print("Kicked Null/non-null")
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                print("Kicked wrong var")
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                print("Kicked wrong var")
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCANADA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=12)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                print("Kicked wrong loc")
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCHILE WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELGREENLAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]

                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELICELAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELPAKISTAN WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])
                        # If the First location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELUNITEDSTATESOFAMERICA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        ## Graph Two

                        # If the Second location is Canada, then create this particular graph

                        if locationTwo == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)
                            elif variableOne == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCANADA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Chile, then create this particular graph
                        elif locationTwo == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCHILE WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Greenland, then create this particular graph
                        elif locationTwo == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELGREENLAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Iceland, then create this particular graph
                        elif locationTwo == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELICELAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Pakistan, then create this particular graph
                        elif locationTwo == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELPAKISTAN WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                        # If the Second location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELUNITEDSTATESOFAMERICA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Compile the Two Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data

                        # Graph Three graphs both of the variable values to eachother, allowing the user to view the correlation of each data value by viewing the data through a different type of plot: a 2d histogram plot
                        if locationTwo == "None":
                            locationTwo = locationOne

                        elif variableTwo == "None":
                            variableTwo = variableOne

                        if variableOne == "Sea Level" or variableTwo == "Sea Level":
                            if locationOne != locationTwo:
                                df = pd.read_sql_query(f"SELECT ROUND(AVG({variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE Average_Annual_Anomaly IS NOT NULL AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                            elif not (variableOne == variableTwo):
                                df = pd.read_sql_query(f"SELECT ROUND(AVG({variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE Average_Annual_Anomaly IS NOT NULL AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                            else:
                                # This is a special case in the code in which the table name is not unique, therefore the "Year" variable cannot be called in the program. Therefore, a statistical variable cannot be determined from the data and the user is notified.
                                statisticalMethodData = "Notice: The third graph pulls from data from the same graph twice, thus could not be created within the specified year range. The third graph has a strong correlation with the variables and locations being the same." + statisticalMethodData
                        elif variableOne == variableTwo and locationOne == locationTwo:
                            # This is a special case in the code in which the table name is not unique, therefore the "Year" variable cannot be called in the program. Therefore, a statistical variable cannot be determined from the data and the user is notified.
                            statisticalMethodData = "Notice: The third graph pulls from data from the same graph twice, thus could not be created within the specified year range. The third graph has a strong correlation with the variables and locations being the same." + statisticalMethodData
                        elif variableOne == variableTwo:
                            df = pd.read_sql_query(f"SELECT {locationByVariableDictionary[variableOne][locationOne]}.{variableTypeDictionary[variableOne]} AS 'graphOneVariable', {locationByVariableDictionary[variableOne][locationTwo]}.{variableTypeDictionary[variableTwo]} AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year",conn)
                        else:
                            df = pd.read_sql_query(f"SELECT ROUND(AVG({locationByVariableDictionary[variableOne][locationOne]}.{variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({locationByVariableDictionary[variableTwo][locationTwo]}.{variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                        if not (isInteger(yearStart) or isInteger(yearEnd)):
                            print("Kicked nonint year two")
                            return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # Add the Scatterplot of the Data to the Subplot Figure
                        if variableOne != variableTwo or locationOne != locationTwo:
                            fig.add_histogram2d(x=df["graphOneVariable"], y=df["graphTwoVariable"], row=1, col=3, nbinsx=30, nbinsy=30)
                        else:
                            fig.add_histogram2d(x=df[variableTypeDictionary[variableOne]], y=df[variableTypeDictionary[variableOne]], row=1, col=3, nbinsx=30, nbinsy=30)

                        # Change the Axes to Clearly Represent the Data and the Time for each Plot
                        if locationOne != locationTwo:
                            fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text=variableOne, row=1, col=3)
                            fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text=variableTwo, row=1, col=3)
                        fig.update_layout(showlegend=False, title_font_size=1210)

                        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template("dataOneVariableTwoLocation.html", graphJSON=graph_json, variableOne = variableOne,
                                               locationOne = locationOne, locationTwo=locationTwo, yearStart = yearStart, yearEnd = yearEnd,
                                               statisticalDataPresent = statisticalDataPresent, statisticalMethodData = statisticalMethodData)

                    elif locationTwo == "None" and variableTwo != "None":
                        # Two-Variable One-location Comparison

                        print("Two Variable One Location Graph")

                        # Label each of the graphs by the given variable
                        graphOneTitle = variableOne + " of " + locationOne
                        graphTwoTitle = variableTwo + " of " + locationOne
                        graphThreeTitle = "Correlation of " + variableOne + " and " + variableTwo

                        # Create the figure to output to the system
                        fig = make_subplots(rows=1, cols=3, subplot_titles=[graphOneTitle, graphTwoTitle, graphThreeTitle])

                        ## Graph One

                        # If the first location is Canada, then create this particular graph
                        if locationOne == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                print("Two-Two, Glacial Canada")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                print(df_given_year['Year'])
                                print(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCANADA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCHILE WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELGREENLAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELICELAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELPAKISTAN WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])
                        # If the First location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT MAX(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT MIN(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT AVG(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT COUNT(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT SUM(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELUNITEDSTATESOFAMERICA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        ## Graph Two

                        # If the Second location is Canada, then create this particular graph

                        if locationOne == locationTableNames[0][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)
                            elif variableTwo == "Surface Temperature Average":
                                print("Two-Two Two Surface Temp Canada")
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCANADA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                print("Years:\n")
                                print(df_given_year['Year'])
                                print("Means:\n")
                                print(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCANADA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCHILE WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELGREENLAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELICELAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELPAKISTAN WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                        # If the Second location is the United States of America, then create this particular graph
                        else:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELUNITEDSTATESOFAMERICA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                        # Graph Three graphs both of the variable values to eachother, allowing the user to view the correlation of each data value by viewing the data through a different type of plot: a 2d histogram plot
                        if locationTwo == "None":
                            locationTwo = locationOne

                        elif variableTwo == "None":
                            variableTwo = variableOne

                        if variableOne == "Sea Level" or variableTwo == "Sea Level":
                            if variableOne != variableTwo:
                                df = pd.read_sql_query(f"SELECT ROUND(AVG({variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE Average_Annual_Anomaly IS NOT NULL AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                            else:
                                # This is a special case in the code in which the table name is not unique, therefore the "Year" variable cannot be called in the program. Therefore, a statistical variable cannot be determined from the data and the user is notified.
                                statisticalMethodData = "Notice: The third graph pulls from data from the same graph twice, thus could not be created within the specified year range. The third graph has a strong correlation with the variables and locations being the same." + statisticalMethodData
                        elif variableOne == variableTwo and locationOne == locationTwo:
                            # This is a special case in the code in which the table name is not unique, therefore the "Year" variable cannot be called in the program. Therefore, a statistical variable cannot be determined from the data and the user is notified.
                            statisticalMethodData = "Notice: The third graph pulls from data from the same graph twice, thus could not be created within the specified year range. The third graph has a strong correlation with the variables and locations being the same." + statisticalMethodData
                        elif variableOne == variableTwo:
                            df = pd.read_sql_query(f"SELECT {locationByVariableDictionary[variableOne][locationOne]}.{variableTypeDictionary[variableOne]} AS 'graphOneVariable', {locationByVariableDictionary[variableOne][locationTwo]}.{variableTypeDictionary[variableTwo]} AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                        else:
                            df = pd.read_sql_query(f"SELECT ROUND(AVG({locationByVariableDictionary[variableOne][locationOne]}.{variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({locationByVariableDictionary[variableTwo][locationTwo]}.{variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                        if not (isInteger(yearStart) or isInteger(yearEnd)):
                            return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # Add the Scatterplot of the Data to the Subplot Figure
                        if variableOne != variableTwo or locationOne != locationTwo:
                            fig.add_histogram2d(x=df["graphOneVariable"], y=df["graphTwoVariable"], row=1, col=3, nbinsx=30, nbinsy=30)
                        else:
                            fig.add_histogram2d(x=df[variableTypeDictionary[variableOne]], y=df[variableTypeDictionary[variableTwo]], row=1, col=3, nbinsx=30, nbinsy=30)

                        # Change the Axes to Clearly Represent the Data and the Time for each Plot
                        fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text=variableOne, row=1, col=3)
                        fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text=variableTwo, row=1, col=3)
                        fig.update_layout(showlegend=False, title_font_size=1210)

                        # Compile the Three Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template("dataTwoVariableOneLocation.html", graphJSON=graph_json, variableOne=variableOne,
                                               variableTwo=variableTwo, locationOne=locationOne, yearStart=yearStart,
                                               yearEnd=yearEnd, statisticalMethodData = statisticalMethodData)

                    elif variableTwo != "None" and variableOne != "None":
                        # Two-Variable Two-Location Comparison
                        print("Two-Variable Two-Location Comparison")
                        # Label each of the graphs by the given variable
                        graphOneTitle = variableOne + " of " + locationOne
                        graphTwoTitle = variableTwo + " of " + locationTwo
                        graphThreeTitle = "Correlation of " + variableOne + " and " + variableTwo

                        # Create the figure to output to the system
                        fig = make_subplots(rows=1, cols=3, subplot_titles=[graphOneTitle, graphTwoTitle, graphThreeTitle])

                        ## Graph One

                        # If the first location is Canada, then create this particular graph
                        if locationOne == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCANADA", conn)
                                print(isInteger(yearStart))
                                print(isInteger(yearEnd))
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCANADA", conn)
                                print(isInteger(yearStart))
                                print(isInteger(yearEnd))
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCANADA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                print("Annual Mean Values in Graph #1: ")
                                print(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCHILE WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELGREENLAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELICELAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        # If the First location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData)
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Annual_Mean), 2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Annual_Mean),2) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])



                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELPAKISTAN WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])
                        # If the First location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT MAX(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT MIN(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT AVG(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT COUNT(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT SUM(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                            elif variableOne == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELUNITEDSTATESOFAMERICA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                                # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                                if statisticalMethodToAdd != "NULL":
                                    # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                    if statisticalMethodToAdd == "Maximum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[ 0][0]
                                        statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Minimum Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                        statisticalMethodData = statisticalMethodData[0][0]
                                        statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Mean Value":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Count":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "Sum":
                                        statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                        statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                        statisticalDataPresent = 1

                                    elif statisticalMethodToAdd == "NULL":
                                        return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        ## Graph Two

                        # If the Second location is Canada, then create this particular graph

                        if locationTwo == locationTableNames[0][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df_given_year = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCANADA", conn)
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCANADA", conn)
                                print(isInteger(yearStart))
                                print(isInteger(yearEnd))
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCANADA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                print(isInteger(yearStart))
                                print(isInteger(yearEnd))
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the First location is Chile, then create this particular graph
                        elif locationTwo == locationTableNames[1][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONCHILE", conn)
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESCHILE", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]

                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELCHILE WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the Second location is Greenland, then create this particular graph
                        elif locationTwo == locationTableNames[2][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESGREENLAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELGREENLAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)


                        # If the First location is Iceland, then create this particular graph
                        elif locationTwo == locationTableNames[3][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESICELAND", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELICELAND WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                        # If the Second location is Pakistan, then create this particular graph
                        elif locationTwo == locationTableNames[4][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESPAKISTAN", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELPAKISTAN WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                        # If the Second location is the United States of America, then create this particular graph
                        else:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM GLACIALELEVATIONUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range = [yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM TEMPERATURESUNITEDSTATESOFAMERICA", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Temperature (Celsius)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                            elif variableTwo == "Sea Level":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                conn = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM SEALEVELUNITEDSTATESOFAMERICA WHERE Average_Annual_Anomaly IS NOT NULL", conn)
                                if not (isInteger(yearStart) or isInteger(yearEnd)):
                                    return render_template("homePage.html", invalidInput=1, authorizedUser = _USER_INFO_LEVEL[0])
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)
                                fig.update_layout(showlegend=False, title_font_size=1210)

                        # Graph Three graphs both of the variable values to eachother, allowing the user to view the correlation of each data value by viewing the data through a different type of plot: a 2d histogram plot

                        if variableOne == "Sea Level" or variableTwo == "Sea Level":
                            if locationOne != locationTwo:
                                df = pd.read_sql_query(f"SELECT ROUND(AVG({variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE Average_Annual_Anomaly IS NOT NULL AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                            elif not (variableOne == variableTwo):
                                df = pd.read_sql_query(f"SELECT ROUND(AVG({variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE Average_Annual_Anomaly IS NOT NULL AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                            else:
                                # This is a special case in the code in which the table name is not unique, therefore the "Year" variable cannot be called in the program. Therefore, a statistical variable cannot be determined from the data and the user is notified.
                                statisticalMethodData = "Notice: The third graph pulls from data from the same graph twice, thus could not be created within the specified year range. The third graph has a strong correlation with the variables and locations being the same." + statisticalMethodData
                        elif variableOne == variableTwo and locationOne == locationTwo:
                            # This is a special case in the code in which the table name is not unique, therefore the "Year" variable cannot be called in the program. Therefore, a statistical variable cannot be determined from the data and the user is notified.
                            statisticalMethodData = "Notice: The third graph pulls from data from the same graph twice, thus could not be created within the specified year range. The third graph has a strong correlation with the variables and locations being the same." + statisticalMethodData
                        elif variableOne == variableTwo:
                            df = pd.read_sql_query(f"SELECT {locationByVariableDictionary[variableOne][locationOne]}.{variableTypeDictionary[variableOne]} AS 'graphOneVariable', {locationByVariableDictionary[variableOne][locationTwo]}.{variableTypeDictionary[variableTwo]} AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                        else:
                            df = pd.read_sql_query(f"SELECT ROUND(AVG({locationByVariableDictionary[variableOne][locationOne]}.{variableTypeDictionary[variableOne]}),2) AS 'graphOneVariable', ROUND(AVG({locationByVariableDictionary[variableTwo][locationTwo]}.{variableTypeDictionary[variableTwo]}),2) AS 'graphTwoVariable', {locationByVariableDictionary[variableTwo][locationTwo]}.Year FROM {locationByVariableDictionary[variableOne][locationOne]} JOIN {locationByVariableDictionary[variableTwo][locationTwo]} ON {locationByVariableDictionary[variableOne][locationOne]}.Year = {locationByVariableDictionary[variableTwo][locationTwo]}.Year WHERE {locationByVariableDictionary[variableTwo][locationTwo]}.Year > {yearStart} AND {locationByVariableDictionary[variableTwo][locationTwo]}.Year < {yearEnd} GROUP BY {locationByVariableDictionary[variableTwo][locationTwo]}.Year", conn)
                        if not (isInteger(yearStart) or isInteger(yearEnd)):
                            return render_template("homePage.html", invalidInput=1,authorizedUser=_USER_INFO_LEVEL[0])

                        # Add the Scatterplot of the Data to the Subplot Figure
                        if variableOne != variableTwo or locationOne != locationTwo:
                            fig.add_histogram2d(x=df["graphOneVariable"], y=df["graphTwoVariable"], row=1, col=3, nbinsx=30, nbinsy=30)
                        else:
                            fig.add_histogram2d(x=df[variableTypeDictionary[variableOne]], y=df[variableTypeDictionary[variableTwo]], row=1, col=3, nbinsx=30, nbinsy=30)

                        # Change the Axes to Clearly Represent the Data and the Time for each Plot
                        fig.update_xaxes(title_font={"size": 10}, position=0.2, title_text=variableOne, row=1, col=3)
                        fig.update_yaxes(title_font={"size": 10}, position=0.2, title_text=variableTwo, row=1, col=3)
                        fig.update_layout(showlegend=False, title_font_size=12)

                        # Compile the Three Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template("dataTwoVariableTwoLocation.html", graphJSON=graph_json, variableOne=variableOne,
                                               variableTwo=variableTwo, locationOne=locationOne, locationTwo=locationTwo,
                                               yearStart=yearStart, yearEnd=yearEnd, statisticalMethodData = statisticalMethodData)
                    else:
                        # One-Variable One-Location Description
                        print("One Var, One Loc")
                        # Initalize the data of the Plot, checking whether the data is within the
                        # starting and ending years given by the user as well as sorting the
                        # variables in the case of Glacial Density.
                        if variableOne == "Glacial Elevation":
                            locationDatabaseName =f"SELECT * FROM glacialElevation" + locationOne

                            # Initalize the data of the Plot, checking whether the data is within the
                            # starting and ending years given by the user as well as sorting the
                            # variables in the case of Glacial Density.
                            conn = sqlite3.connect("climateChangeDatabase.db")
                            df = pd.read_sql_query(locationDatabaseName, conn)
                            if not (isInteger(yearStart) or isInteger(yearEnd)):
                                return render_template("homePage.html", invalidInput = 1, authorizedUser=_USER_INFO_LEVEL[0])
                            df_given_year = df[df["Year"] >= yearStart]
                            df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                            df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])

                            # Add the Scatterplot of the Data to the Subplot Figure
                            fig = px.scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], labels={'x': 'Years', 'y': 'Average Change in Measured GlacierElevation (mm)'})

                            # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                            if statisticalMethodToAdd != "NULL":
                                # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                if statisticalMethodToAdd == "Maximum Value":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Highest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Minimum Value":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Lowest Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Mean Value":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Mean Glacial Elevation Difference between Survey Date and Reference Date Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Count":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Total Glacial Elevation Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Sum":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Glacial_Density),2) FROM GLACIALELEVATION{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Total Sum of Glacial Elevation Differences Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "NULL":
                                    return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        elif variableOne == "Surface Temperature Average":

                            locationDatabaseName = f"SELECT * FROM temperatures" + locationOne + "Two"

                            # Initalize the data of the Plot, checking whether the data is within the
                            # starting and ending years given by the user as well as sorting the
                            # variables in the case of Glacial Density.
                            conn = sqlite3.connect("climateChangeDatabase.db")
                            df = pd.read_sql_query(locationDatabaseName, conn)
                            df_given_year = df[df["Year"] >= yearStart]
                            df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                            xVar = list(df_given_year['Year'])
                            yVar = list(df_given_year['Annual_Mean'])

                            # Add the Scatterplot of the Data to the Subplot Figure
                            fig = px.scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], labels={'x': 'Years', 'y': 'Average Annual Temperature (Degrees Celsius)'})

                            # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                            if statisticalMethodToAdd != "NULL":
                                # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                if statisticalMethodToAdd == "Maximum Value":
                                    statisticalMethodData = cur.execute(f"SELECT MAX(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Highest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Minimum Value":
                                    statisticalMethodData = cur.execute(f"SELECT MIN(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Lowest Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Mean Value":
                                    statisticalMethodData = cur.execute(f"SELECT AVG(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Mean Temperature Average Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Count":
                                    statisticalMethodData = cur.execute(f"SELECT COUNT(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Total Temperature Average Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Sum":
                                    statisticalMethodData = cur.execute(f"SELECT SUM(Annual_Mean) FROM TEMPERATURES{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Total Sum of Temperature Averages Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " Degrees Celsius"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "NULL":
                                    return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                        elif variableOne == "Sea Level":

                            locationDatabaseName = f"SELECT * FROM temperatures" + locationOne + "Two"

                            # Initalize the data of the Plot, checking whether the data is within the
                            # starting and ending years given by the user as well as sorting the
                            # variables in the case of Glacial Density.
                            conn = sqlite3.connect("climateChangeDatabase.db")
                            df = pd.read_sql_query(locationDatabaseName, conn)
                            df_given_year = df[df["Year"] >= yearStart]
                            df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                            xVar = list(df_given_year['Year'])
                            yVar = list(df_given_year['Average_Annual_Anomaly'])

                            # Add the Scatterplot of the Data to the Subplot Figure
                            fig = px.scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], labels={'x': 'Years', 'y': 'Average Annual Sea Level Change (mm)'})

                            # Statistical Method Data determines by the requested method, does not evaluate the data if the method entry is null
                            if statisticalMethodToAdd != "NULL":
                                # Determine which statistical method the user wishes to use, then output the description of the statistical method's findings to the UI
                                if statisticalMethodToAdd == "Maximum Value":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(MAX(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Highest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Minimum Value":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(MIN(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()
                                    statisticalMethodData = statisticalMethodData[0][0]
                                    statisticalMethodData = "Lowest Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Mean Value":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(AVG(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Mean Annual Sea Level Anomaly Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Count":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(COUNT(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Total Annual Sea Level Anomaly Entries Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "Sum":
                                    statisticalMethodData = cur.execute(f"SELECT ROUND(SUM(Average_Annual_Anomaly),2) FROM SEALEVEL{locationOne} WHERE Year >= {yearStart} AND Year <= {yearEnd}").fetchall()[0][0]
                                    statisticalMethodData = "Total Sum of Annual Sea Level Anomalies Found in " + locationOne + " between " + str(yearStart) + " and " + str(yearEnd) + ": " + str(statisticalMethodData) + " mm"
                                    statisticalDataPresent = 1

                                elif statisticalMethodToAdd == "NULL":
                                    return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])
                        else:
                            print("Kicked end")
                            return render_template("homePage.html", invalidInput=1, authorizedUser=_USER_INFO_LEVEL[0])

                    # Compile the Two Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    return render_template("dataOneVariableOneLocation.html", graphJSON=graph_json, variableOne=variableOne,
                                           locationOne=locationOne, yearStart=yearStart, yearEnd=yearEnd, statisticalMethodData = statisticalMethodData)
            else:
                print("Kicked Very End")
                return render_template("homePage.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 0, authorizedUser=_USER_INFO_LEVEL[0])
        print("Current End")
        return render_template("homePage.html", graphingAuthorized=0, petitionAuthorized=0, invalidInput=0, authorizedUser=_USER_INFO_LEVEL[0])