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
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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

locationTableNames = [["Canada", "glacialElevationCanada", "temperaturesCanadaTwo", "seaLevelCanadaTwo"],
                     ["Chile", "glacialElevationChile", "temperaturesChileTwo", "seaLevelChileTwo"],
                     ["Greenland", "glacialElevationGreenland", "temperaturesGreenlandTwo", "seaLevelGreenlandTwo"],
                     ["Iceland", "glacialElevationIceland", "temperaturesIcelandTwo", "seaLevelIcelandTwo"],
                     ["Pakistan", "glacialElevationPakistan", "temperaturesPakistanTwo", "seaLevelPakistanTwo"],
                     ["United States of America", "glacialElevationUnitedStates", "temperaturesUnitedStatesOfAmericaTwo", "seaLevelUnitedStatesOfAmericaTwo"]]

# TODO: Edge case for same username and password not returning the error message, lower priority!
# TODO: Fix Background image for the Login Screen of the Website (Flask issue)
# TODO: Immediately change the HTML link for the title page to 127.0.0.1/home_page V

# To test if the value inputted is a valid input, we must test if any type of number is a float
# or an integer. We will do this with a "try-except" block from the following source:
# https://www.programiz.com/python-programming/examples/check-string-number
def isFloat(item):
    try:
        float(item)
        return True
    except ValueError:
        return False

def isInteger(item):
    try:
        int(item)
        return True
    except ValueError:
        return False

@app.route('/', methods=['GET', 'POST'])
def climateChangeUserInterfaceLogin():

    validUser = 0

    username = request.form.get("username", string)
    password = request.form.get("password", string)
    nullInputString = request.form.get("nullInput", string)

    for userData in validUserInformation:
        if userData[0] == username and userData[1] == password:
            validUser = 1

    # Check if the user is the admin, and if so set their "userInfoLevel" to 1.
    if username == "adminRocks031" and password == "4dm1n71m3!":
        userInfoLevel = 1

    # Previous login is 0 WHEN the user has logged in before
    # ValidUser is 1 when the user has entered in the correct password, and is 0 when they have not

    if username == nullInputString or password == nullInputString:
        return render_template("login.html", invalidInput = 0)
    elif validUser == 0:
        return render_template("login.html", invalidInput = 1)
    elif validUser == 1:
        return redirect('/home_page')

# TODO: Fix Variables being accepted for
# TODO: Create a hope page for petitions for new countries to add to the registry that specifically petitions from a given user on the homepage front!
# TODO: Create an interface for the graphing segment, possibly make it another drop-down from the off of the home page
# TODO: Create a pointer variable that allows the website to determine when the user is the admin, then create a drop-down that allows for the admin to add, remove, and replace specific information in the registry
# TODO: Make the Home Page look nice by formatting the page (CSS when necessary, HTML as much as I can)!

@app.route('/petition_input', methods=['GET', 'POST'])
def climateChangeUserInterfacePetitionPage():
    return redirect('/home_page')

@app.route('/admin_input', methods=['GET', 'POST'])
def climateChangeUserInterfaceInputPage():

    conn = sqlite3.connect('climateChangeDatabase.db')
    cur = conn.cursor()

    # TODO: Complete and Test "ADD MODIFY REMOVE" Functionaly and "QUERY UNDER CONDITIONS"

    # Collect each of the pieces of info from the HTML Website, including of
    # data to modify and which section of the database the data is.
    locationToEdit = request.form.get("locationToEdit", string)
    variableType = request.form.get("variableType", string)
    valueInDatabase = request.form.get("valueInDatabase", string)
    valueIntoDatabase = request.form.get("valueIntoDatabase", string)
    columnName = request.form.get("columnName", string)
    rowIndex = request.form.get("rowIndex", string)
    replacementType = request.form.get("replacementType", string)
    returnToHome = request.form.get("returnToHome", string)

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

        if locationToEdit == nullValueString or variableType == nullValueString or (valueInDatabase == nullValueString and valueIntoDatabase == nullValueString) or columnName == nullValueString or rowIndex == nullValueString:
            return render_template("input.html", invalidInput = 1, completedInput = 0)

        if replacementType == "Modify":

            if variableType == "Glacial Density" and (columnName == "Glacial_Density" or columnName == "Year") and rowIndex.isdigit() and int(rowIndex) >= 0 and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "glacialElevation" + locationToEdit
                rowMax = cur.execute(f"SELECT max(elevation_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput = 1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = {valueIntoDatabase} WHERE 'elevation_id' = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput = 0, completedInput = 1)
            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth") and rowIndex.isdigit() and int(rowIndex) >= 0 and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):

                tableName = "temperatures" + locationToEdit + "Two"
                rowMax = cur.execute(f"SELECT max(temperature_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):

                    return render_template("input.html", invalidInput = 1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE {tableName} SET {columnName} = {valueIntoDatabase} WHERE 'temperature_id' = {int(rowIndex)}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Sea Level" and (((columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase))) or (columnName == "Month")) and rowIndex.isdigit() and int(rowIndex) >= 0:
                tableName = "seaLevel" + locationToEdit + "Two"
                rowMax = cur.execute(f"SELECT max(sea_level_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput = 1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE 'sea_level_id' = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput = 1)
            elif variableType == "User Data" and (columnName == "USERNAME" or columnName == "PASSWORD" or columnName == "DISPLAY_NAME" or columnName == "USER_ACCESS") and rowIndex.isdigit() and int(rowIndex) >= 0:
                tableName = "users"
                rowMax = cur.execute(f"SELECT max(index_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE 'index_id' = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Petition Data" and (columnName == "DISPLAY_NAME" or columnName == "COUNTRY" or columnName == "REASON") and rowIndex.isdigit() and int(rowIndex) > 0:
                tableName = "petitions"
                rowMax = cur.execute(f"SELECT max(index_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput = 0)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE 'index_id' = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            else:
                return render_template("input.html", invalidInput = 1, completedInput = 0)

        elif replacementType == "Remove":
            if variableType == "Glacial Density" and (columnName == "Glacial_Density" or columnName == "Year") and isInteger(rowIndex) and int(rowIndex) >= 0:
                tableName = "glacialElevation" + locationToEdit
                tableNameTemp = "glacialElevationTemp"
                rowMax = cur.execute(f"SELECT max(elevation_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0][0]
                # If the index is invalid, then notify the user
                if rowMax < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)

                # If the row index is valid but no value was entered, then the entire row is removed.
                elif valueInDatabase == nullValueString:
                    print("Here0")
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE 'elevation_id' != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    print(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE 'elevation_id' == {rowIndex}")
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE 'elevation_id' == {rowIndex}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth") and rowIndex.isdigit() and int(rowIndex) >= 0:
                tableName = "temperatures" + locationToEdit + "Two"
                tableNameTemp = "temperaturesTemp"
                rowMax = cur.execute(f"SELECT max(temperature_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == nullValueString:
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE 'temperature_id' != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE 'temperature_id' == '{rowIndex}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Sea Level" and ((columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") or (columnName == "Month")) and rowIndex.isdigit() and int(rowIndex) >= 0:
                tableName = "seaLevel" + locationToEdit + "Two"
                tableNameTemp = "seaLevelTemp"
                rowMax = cur.execute(f"SELECT max(sea_level_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == nullValueString:
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE 'sea_level_id' != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE 'sea_level_id' == '{rowIndex}'")
                    conn.commit()
                    return render_template("input.html", invalidInput = 0, completedInput = 1)
            elif variableType == "User Data" and (columnName == "USERNAME" or columnName == "PASSWORD" or columnName == "DISPLAY_NAME" or columnName == "USER_ACCESS") and rowIndex.isdigit() and int(rowIndex) >= 0:
                tableName = "users"
                tableNameTemp = "usersTemp"
                rowMax = cur.execute(f"SELECT max(user_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == nullValueString:
                    cur.execute(
                        f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE 'user_id' != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE 'user_id' == '{rowIndex}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            elif variableType == "Petition Data" and (columnName == "DISPLAY_NAME" or columnName == "COUNTRY" or columnName == "REASON") and rowIndex.isdigit() and int(rowIndex) > 0:
                tableName = "petitions"
                tableNameTemp = "petitionsTemp"
                rowMax = cur.execute(f"SELECT max(index_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                if rowMax[0] < int(rowIndex):
                    return render_template("input.html", invalidInput=1, completedInput=0)
                elif valueInDatabase == nullValueString:
                    cur.execute(f"CREATE TABLE '{tableNameTemp}' AS SELECT * FROM '{tableName}' WHERE 'index_id' != '{int(rowIndex)}'")
                    cur.execute(f"DROP TABLE '{tableName}'")
                    cur.execute(f"CREATE TABLE '{tableName}' AS SELECT * FROM '{tableNameTemp}'")
                    cur.execute(f"DROP TABLE '{tableNameTemp}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = NULL WHERE 'index_id' == {rowIndex}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
            else:
                return render_template("input.html", invalidInput = 1, completedInput=0)

        # Row index is used to determine if the user wishes to add a new data row, or to add data to an existing row
        elif replacementType == "Add":
            if variableType == "Glacial Density" and (columnName == "Glacial_Density" or columnName == "Year") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "glacialElevation" + locationToEdit
                rowMax = cur.execute(f"SELECT max(elevation_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0][0]
                newRowIndex = int(rowMax) + 1
                # If row is within the database, the value is added to the line of data
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = {valueIntoDatabase} WHERE 'elevation_id' = '{int(rowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)

                # If the row is not within the database, than a new row is created from the existing details if the existing details are correct
                elif rowIndex == "-1":
                    if columnName == "Year":
                        cur.execute(f"INSERT INTO {tableName} ('elevation_id', 'Year', 'Glacial_Density') VALUES ('{newRowIndex}', '{valueIntoDatabase}', NULL)")
                    elif columnName == "Glacial_Density":
                        cur.execute(f"INSERT INTO {tableName} ('elevation_id', 'Year', 'Glacial_Density') VALUES ('{newRowIndex}', 2022, '{valueIntoDatabase}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput = 1, completedInput = 0)

            elif variableType == "Average Surface Temperature" and (columnName == "Annual_Mean" or columnName == "Year" or columnName == "Five_Year_Smooth") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase)):
                tableName = "temperatures" + locationToEdit + "Two"
                rowMax = cur.execute(f"SELECT max(temperature_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0][0]
                newRowIndex = int(rowMax) + 1
                # If row is within the database, the value is added to the line of data
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE {tableName} SET {columnName} = {valueIntoDatabase} WHERE 'temperature_id' = {int(newRowIndex)}")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)

                # If the row is not within the database, than a new row is created from the existing details if the existing details are correct
                elif rowIndex == "-1":
                    if columnName == "Annual_Mean":
                        cur.execute(f"INSERT INTO {tableName} ('temperature_id', 'Year', 'Annual_Mean', 'Five_Year_Smooth') VALUES ('{newRowIndex}', NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "Year":
                        cur.execute(f"INSERT INTO {tableName} ('temperature_id', 'Year', 'Annual_Mean', 'Five_Year_Smooth') VALUES ('{newRowIndex}', '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "Five_Year_Smooth":
                        cur.execute(f"INSERT INTO {tableName} ('temperature_id', 'Year', 'Annual_Mean', 'Five_Year_Smooth') VALUES ('{newRowIndex}', NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)

            elif variableType == "Sea Level" and (((columnName == "Year" or columnName == "Average_Monthly_Anomaly" or columnName == "Average_Annual_Anomaly") and (isFloat(valueIntoDatabase) or isInteger(valueIntoDatabase))) or (columnName == "Month")):
                tableName = "seaLevel" + locationToEdit + "Two"
                rowMax = cur.execute(f"SELECT max(sea_level_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                newRowIndex = int(rowMax[0]) + 1
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE 'sea_level_id' = '{int(newRowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                elif rowIndex == "-1":
                    if columnName == "Month":
                        cur.execute(f"INSERT INTO {tableName} ('sea_level_id', 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', '{valueIntoDatabase}', NULL, NULL, NULL)")
                    elif columnName == "Year":
                        cur.execute(f"INSERT INTO {tableName} ('sea_level_id', 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', NULL, '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "Average_Monthly_Anomaly":
                        cur.execute(f"INSERT INTO {tableName} ('sea_level_id', 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', NULL, NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "Average_Annually_Anomaly":
                        cur.execute(f"INSERT INTO {tableName} ('sea_level_id', 'Month', 'Year', 'Average_Monthly_Anomaly', 'Average_Annual_Anomaly') VALUES ('{newRowIndex}', NULL, NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)
            elif variableType == "User Data" and (columnName == "USERNAME" or columnName == "PASSWORD" or columnName == "DISPLAY_NAME" or columnName == "USER_ACCESS"):
                tableName = "users"
                rowMax = cur.execute(f"SELECT max(index_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                newRowIndex = int(rowMax[0]) + 1
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE 'index_id' = '{int(newRowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                elif rowIndex == "-1":
                    if columnName == "USERNAME":
                        cur.execute(f"INSERT INTO {tableName} ('user_id', 'LOGIN_ID' 'USERNAME', 'PASSWORD', 'DISPLAY_NAME', 'USER_ACCESS') VALUES ('{newRowIndex}', '{newRowIndex + 1}', '{valueIntoDatabase}', NULL, NULL, NULL)")
                    elif columnName == "PASSWORD":
                        cur.execute(f"INSERT INTO {tableName} ('user_id', 'LOGIN_ID' 'USERNAME', 'PASSWORD', 'DISPLAY_NAME', 'USER_ACCESS') VALUES ('{newRowIndex}', '{newRowIndex + 1}', NULL, '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "DISPLAY_NAME":
                        cur.execute(f"INSERT INTO {tableName} ('user_id', 'LOGIN_ID' 'USERNAME', 'PASSWORD', 'DISPLAY_NAME', 'USER_ACCESS') VALUES ('{newRowIndex}', '{newRowIndex + 1}', NULL, NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "USER_ACCESS":
                        cur.execute(f"INSERT INTO {tableName} ('user_id', 'LOGIN_ID' 'USERNAME', 'PASSWORD', 'DISPLAY_NAME', 'USER_ACCESS') VALUES ('{newRowIndex}', '{newRowIndex + 1}', NULL, NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)
            elif variableType == "Petition Data" and (columnName == "DISPLAY_NAME" or columnName == "COUNTRY" or columnName == "REASON"):
                tableName = "petitions"
                rowMax = cur.execute(f"SELECT max(index_id) FROM '{tableName}'").fetchall()
                rowMax = rowMax[0]
                newRowIndex = int(rowMax[0]) + 1
                if isInteger(rowIndex) and (int(rowIndex) >= 0 and rowMax >= int(rowIndex)):
                    cur.execute(f"UPDATE '{tableName}' SET '{columnName}' = '{valueIntoDatabase}' WHERE 'index_id' = '{int(newRowIndex)}'")
                    conn.commit()
                    return render_template("input.html", invalidInput=0, completedInput=1)
                elif rowIndex == "-1":
                    if columnName == "DISPLAY_NAME":
                        cur.execute(f"INSERT INTO {tableName} ('index_id', 'PETITION_ID' 'DISPLAY_NAME', 'COUNTRY', 'REASON') VALUES ('{newRowIndex}', '{newRowIndex}', '{valueIntoDatabase}', NULL, NULL)")
                    elif columnName == "COUNTRY":
                        cur.execute(f"INSERT INTO {tableName} ('index_id', 'PETITION_ID' 'DISPLAY_NAME', 'COUNTRY', 'REASON') VALUES ('{newRowIndex}', '{newRowIndex}', NULL, '{valueIntoDatabase}', NULL)")
                    elif columnName == "REASON":
                        cur.execute(f"INSERT INTO {tableName} ('index_id', 'PETITION_ID' 'DISPLAY_NAME', 'COUNTRY', 'REASON') VALUES ('{newRowIndex}', '{newRowIndex}', NULL, NULL, '{valueIntoDatabase}')")
                    conn.commit()
                    return render_template("input.html", invalidInput=1, completedInput=0)
                else:
                    return render_template("input.html", invalidInput=1, completedInput=0)
            else:
                return render_template("input.html", invalidInput=1, completedInput=0)
    else:
        return render_template("input.html", invalidInput = 0, completedInput = 0)



@app.route('/home_page', methods=['GET', 'POST'])
def climateChangeUserInterfaceHomePage():

    locationOne = request.form.get("locationOne", string)
    locationTwo = request.form.get("locationTwo", string)
    variableOne = request.form.get("variableOne", string)
    variableTwo = request.form.get("variableTwo", string)
    yearStart = request.form.get("yearStart", int)
    yearEnd = request.form.get("yearEnd", int)
    exampleNumber = request.form.get("exampleNumber", string)
    inputType = request.form.get("inputType", string)
    statisticalMethodToAdd = request.form.get("statisticalMethodToAdd", string)
    statisticalMethodVariableName = request.form.get("statisticalMethodVariableName", string)

    nullValueInt = request.form.get("nullValueInt", int)
    nullValueString = request.form.get("nullValueString", string)

    print(locationOne)
    print(locationTwo)
    print(variableOne)
    print(variableTwo)
    print(yearStart)
    print(yearEnd)
    print(userInfoLevel)
    print(exampleNumber)
    print(inputType)

    if request.method == "GET":
        return render_template("title.html", authorizedUser = 1, invalidInput = 0)

    a = """
    if request.method == 'GET':
        fig = make_subplots(rows=1, cols=2)

        con = sqlite3.connect("climateChangeDatabase.db")
        df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= {}", con)
        df_given_year = df[df["Year"] >= yearStart]
        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
        df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
        xVar = list(df_given_year['Year'])
        yVar = list(df_given_year['Glacial_Density'])

        fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)
        
        # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Density of Glacia1 Ice (mm)", row=1, col=1)

        con = sqlite3.connect("climateChangeDatabase.db")
        df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo", con)
        df_given_year = df[df["Year"] >= yearStart]
        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
        df_given_year = df_given_year[df_given_year["Month"] == "Jan"]
        df_given_year = df_given_year.sort_values(by=["Year", "Average_Annual_Anomaly"])
        xVar = list(df_given_year['Year'])
        yVar = list(df_given_year['Average_Annual_Anomaly'])

        fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("dataOneVariableOneLocation.html", graphJSON = graph_json)
    elif request == "POST":
        fig = make_subplots(rows=1, cols=2)

        con = sqlite3.connect("climateChangeDatabase.db")
        df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= {}"", con)
        df_given_year = df[df["Year"] >= yearStart]
        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
        df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
        xVar = list(df_given_year['Year'])
        yVar = list(df_given_year['Glacial_Density'])

        fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'])

        con = sqlite3.connect("climateChangeDatabase.db")
        df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica", con)
        df_given_year = df[df["Year"] >= yearStart]
        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
        df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
        xVar = list(df_given_year['Year'])
        yVar = list(df_given_year['Glacial_Density'])

        fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'])

        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template("dataOneLocationTwoVariable.html", graphJSON = graph_json)
        #return render_template("title.html", graphingAuthorized=0, petitionAuthorized=0, invalidInput=0)
    else:
        fig = make_subplots(rows=1, cols=2)

        con = sqlite3.connect("climateChangeDatabase.db")
        df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= {}" con)
        df_given_year = df[df["Year"] >= yearStart]
        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
        df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
        xVar = list(df_given_year['Year'])
        yVar = list(df_given_year['Glacial_Density'])

        fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'])

        con = sqlite3.connect("climateChangeDatabase.db")
        df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica", con)
        df_given_year = df[df["Year"] >= yearStart]
        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
        df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
        xVar = list(df_given_year['Year'])
        yVar = list(df_given_year['Glacial_Density'])

        fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'])
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("dataOneLocationTwoVariable.html", graphJSON = graph_json)
        #return render_template("title.html", graphingAuthorized=0, petitionAuthorized=0, invalidInput=0)
"""
    if request.method == 'POST':

        if inputType == "petition":
            return redirect('/petition_input')

        elif inputType == "adminInput":
            return redirect('/admin_input')

            # TODO: Show Graphs is Three Different Forms to present Join Queries
            # TODO: Create an option to print Statistical Methods with the graph!
            # TODO: Create an option to show the different examples if there is time!

        else:
            if yearStart != nullValueInt and yearEnd != nullValueInt:
                yearStart = int(yearStart)
                yearEnd = int(yearEnd)
            # Return an error message on the site if the user entered an invalid year
            if yearStart != nullValueInt and yearEnd != nullValueInt:
                if (int(yearStart) < 1900 or int(yearEnd) > 2021):
                    return render_template("title.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 1)

            # If neither variableOne or locationOne are null values, then we can create a valid graph or series of graphs.
            if variableOne != nullValueString and locationOne != nullValueString and yearStart != nullValueInt and yearEnd != nullValueInt:
                if variableTwo != locationTwo:
                    if variableTwo == nullValueString:
                        # One-Variable Two-Location Comparison

                        # Label each of the graphs by the given variable
                        graphOneTitle = variableOne + " of " + locationOne
                        graphTwoTitle = variableOne + " of " + locationTwo

                        # Create the figure to output to the system
                        fig = make_subplots(rows=1, cols=2, subplot_titles = [graphOneTitle, graphTwoTitle])

                        ## Graph One

                        # If the first location is Canada, then create this particular graph
                        if locationOne == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationChile WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}' WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationGreenland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationIceland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationPakistan WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                        # If the First location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        ## Graph Two

                        # If the Second location is Canada, then create this particular graph

                        if locationTwo == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                            elif variableOne == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the First location is Chile, then create this particular graph
                        elif locationTwo == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationChile WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}' WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the Second location is Greenland, then create this particular graph
                        elif locationTwo == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationGreenland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the First location is Iceland, then create this particular graph
                        elif locationTwo == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationIceland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the Second location is Pakistan, then create this particular graph
                        elif locationTwo == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationPakistan WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)

                        # If the Second location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # Compile the Two Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template("dataOneVariableTwoLocation.html", graphJSON=graph_json, variableOne = variableOne,
                                               locationOne = locationOne, locationTwo=locationTwo, yearStart = yearStart, yearEnd = yearEnd)

                    elif locationTwo == nullValueString:
                        # Two-Variable One-location Comparison

                        # Label each of the graphs by the given variable
                        graphOneTitle = variableOne + " of " + locationOne
                        graphTwoTitle = variableTwo + " of " + locationOne

                        # Create the figure to output to the system
                        fig = make_subplots(rows=1, cols=2, subplot_titles=[graphOneTitle, graphTwoTitle])

                        ## Graph One

                        # If the first location is Canada, then create this particular graph
                        if locationOne == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                            elif variableOne == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationChile WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}' WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationGreenland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationIceland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationPakistan WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                        # If the First location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        ## Graph Two

                        # If the Second location is Canada, then create this particular graph

                        if locationOne == locationTableNames[0][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                            elif variableTwo == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationChile WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}' WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the Second location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationGreenland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationIceland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the Second location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationPakistan WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)

                        # If the Second location is the United States of America, then create this particular graph
                        else:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # Compile the Two Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template("dataTwoVariableOneLocation.html", graphJSON=graph_json, variableOne=variableOne,
                                               variableTwo=variableTwo, locationOne=locationOne, yearStart=yearStart,
                                               yearEnd=yearEnd)

                    else:
                        # Two-Variable Two-Location Comparison

                        # Label each of the graphs by the given variable
                        graphOneTitle = variableOne + " of " + locationOne
                        graphTwoTitle = variableTwo + " of " + locationTwo

                        # Create the figure to output to the system
                        fig = make_subplots(rows=1, cols=2, subplot_titles=[graphOneTitle, graphTwoTitle])

                        ## Graph One

                        # If the first location is Canada, then create this particular graph
                        if locationOne == locationTableNames[0][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)
                            elif variableOne == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Chile, then create this particular graph
                        elif locationOne == locationTableNames[1][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationChile WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Greenland, then create this particular graph
                        elif locationOne == locationTableNames[2][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationGreenland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Iceland, then create this particular graph
                        elif locationOne == locationTableNames[3][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationIceland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        # If the First location is Pakistan, then create this particular graph
                        elif locationOne == locationTableNames[4][0]:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationPakistan WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)
                        # If the First location is the United States of America, then create this particular graph
                        else:

                            if variableOne == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=1)

                            elif variableOne == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=1)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=1)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=1)

                        ## Graph Two

                        # If the Second location is Canada, then create this particular graph

                        if locationTwo == locationTableNames[0][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationCanada WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)
                            elif variableTwo == "Surface Temperature Average":

                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelCanadaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the First location is Chile, then create this particular graph
                        elif locationTwo == locationTableNames[1][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationChile WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelChileTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the Second location is Greenland, then create this particular graph
                        elif locationTwo == locationTableNames[2][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationGreenland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelGreenlandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)


                        # If the First location is Iceland, then create this particular graph
                        elif locationTwo == locationTableNames[3][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationIceland WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelIcelandTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)

                        # If the Second location is Pakistan, then create this particular graph
                        elif locationTwo == locationTableNames[4][0]:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationPakistan WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelPakistanTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)

                        # If the Second location is the United States of America, then create this particular graph
                        else:

                            if variableTwo == "Glacial Elevation":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM glacialElevationUnitedStatesOfAmerica WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Glacial_Density'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=2, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Elevation Change of Glacial Ice Since Given Year (mm)", row=1, col=2)

                            elif variableTwo == "Surface Temperature Average":
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM temperaturesUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Annual_Mean'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Temperature (Celsius)", row=1, col=2)

                            else:
                                # Initalize the data of the Plot, checking whether the data is within the
                                # starting and ending years given by the user as well as sorting the
                                # variables in the case of Glacial Density.
                                con = sqlite3.connect("climateChangeDatabase.db")
                                df = pd.read_sql_query(f"SELECT * FROM seaLevelUnitedStatesOfAmericaTwo WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'", con)
                                df_given_year = df[df["Year"] >= yearStart]
                                df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                                xVar = list(df_given_year['Year'])
                                yVar = list(df_given_year['Average_Annual_Anomaly'])

                                # Add the Scatterplot of the Data to the Subplot Figure
                                fig.add_scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'], row=1, col=2)

                                # Change the Axes to Clearly Represent the Data and the Time for each Plot
                                fig.update_xaxes(title_text="Year", row=1, col=1, range=[yearStart, yearEnd])
                                fig.update_yaxes(title_text="Average Yearly Height Above Global Average Sea Level (mm)", row=1, col=2)

                        # Compile the Two Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template("dataTwoVariableTwoLocation.html", graphJSON=graph_json, variableOne=variableOne,
                                               variableTwo=variableTwo, locationOne=locationOne, locationTwo=locationTwo,
                                               yearStart=yearStart, yearEnd=yearEnd)
                else:
                    # One-Variable One-Location Description

                    # Initalize the data of the Plot, checking whether the data is within the
                    # starting and ending years given by the user as well as sorting the
                    # variables in the case of Glacial Density.


                    if variableOne == "Glacier Density":

                        locationDatabaseName =f"SELECT * FROM glacialElevation" + locationOne + " WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'"

                        # Initalize the data of the Plot, checking whether the data is within the
                        # starting and ending years given by the user as well as sorting the
                        # variables in the case of Glacial Density.
                        con = sqlite3.connect("climateChangeDatabase.db")
                        df = pd.read_sql_query(locationDatabaseName, con)
                        df_given_year = df[df["Year"] >= yearStart]
                        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                        df_given_year = df_given_year.sort_values(by=["Year", "Glacial_Density"])
                        xVar = list(df_given_year['Year'])
                        yVar = list(df_given_year['Glacial_Density'])

                        # Add the Scatterplot of the Data to the Subplot Figure
                        fig = px.scatter(x=df_given_year['Year'], y=df_given_year['Glacial_Density'])

                    elif variableOne == "Surface Temperature Average":

                        locationDatabaseName = f"SELECT * FROM temperatures" + locationOne + "Two" + " WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'"

                        # Initalize the data of the Plot, checking whether the data is within the
                        # starting and ending years given by the user as well as sorting the
                        # variables in the case of Glacial Density.
                        con = sqlite3.connect("climateChangeDatabase.db")
                        df = pd.read_sql_query(locationDatabaseName, con)
                        df_given_year = df[df["Year"] >= yearStart]
                        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                        xVar = list(df_given_year['Year'])
                        yVar = list(df_given_year['Annual_Mean'])

                        # Add the Scatterplot of the Data to the Subplot Figure
                        fig = px.scatter(x=df_given_year['Year'], y=df_given_year['Annual_Mean'])

                    elif variableOne == "Sea Level":

                        locationDatabaseName = f"SELECT * FROM temperatures" + locationOne + "Two" + " WHERE 'Year' >= '{yearStart}' AND 'Year' <= '{yearEnd}'"

                        # Initalize the data of the Plot, checking whether the data is within the
                        # starting and ending years given by the user as well as sorting the
                        # variables in the case of Glacial Density.
                        con = sqlite3.connect("climateChangeDatabase.db")
                        df = pd.read_sql_query(locationDatabaseName, con)
                        df_given_year = df[df["Year"] >= yearStart]
                        df_given_year = df_given_year[df_given_year["Year"] <= yearEnd]
                        xVar = list(df_given_year['Year'])
                        yVar = list(df_given_year['Average_Annual_Anomaly'])

                        # Add the Scatterplot of the Data to the Subplot Figure
                        fig = px.scatter(x=df_given_year['Year'], y=df_given_year['Average_Annual_Anomaly'])


                    # Compile the Two Figures (subplot) in JSON and render the template with the HTML Link of the Figure Data
                    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    return render_template("dataOneVariableOneLocation.html", graphJSON=graph_json, variableOne=variableOne,
                                           locationOne=locationOne, yearStart=yearStart, yearEnd=yearEnd)

        return render_template("title.html", graphingAuthorized = 0, petitionAuthorized = 0, invalidInput = 0)
