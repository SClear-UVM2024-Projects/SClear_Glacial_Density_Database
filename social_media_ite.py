# Log-in Authentication
# Created by: Samuel Clear
# 11/03/2022

import sqlite3
import pandas as pd

# This shows all of the data that has been downloaded into the file!
def dump_data(cur):
    data = cur.execute("SELECT * from users;")
    for tup in data:
        print(tup)

# Conn is the current database file in SQL that will be edited by changes, while "cur" is the current changes that are being made!
conn = sqlite3.connect('usersData.db')
cur = conn.cursor()

# Welcome user to the site and load all of the current login information for authorized users
print("Welcome to Social Media Lite")
authorizedUsers = cur.execute("SELECT * FROM users").fetchall()

# Initially assume that all data entered is false and search the data given for each username and password
authorized = False
while not authorized:

    # Assume that the username and password are not authorized
    usernameAuthorized = False
    passwordAuthorized = False

    # Take user data input from user
    givenUsername = input("Username: ")
    givenPassword = input("Password: ")

    # Evaluate if the input is within the authorized users, authorize the user if so
    for tupleData in authorizedUsers:
        if givenUsername in tupleData:
            usernameAuthorized = True
            if givenPassword in tupleData:
                passwordAuthorized = True

    if not usernameAuthorized:
        print("User not found.")
    elif not passwordAuthorized:
        print("Access Denied.")
    elif usernameAuthorized and passwordAuthorized:
        authorized = True
        print("Successful Login")

# Log in the user
loggedIn = True

# Prompt the user with different interface options until they log off
while loggedIn: # Use cur.fetchall to get a list of tuples!!!
    allUserData = cur.execute(f"SELECT index_id, user_id, email_id, username, password, account_created, first_name, last_name, birth_date FROM users").fetchall()
    for userData in allUserData: # For-loops for some reason will only run once during the program
        if userData[3] == givenUsername and userData[4] == givenPassword:
            dataOfUser = userData
    nameOfUser = dataOfUser[6] + " " + dataOfUser[7]
    mainUserID = dataOfUser[1]

    print(f"Welcome {nameOfUser}\nWhat would you like to do?")
    print(" View User Information (!)\n Look at your posts (?)")
    print(" Find out your Followers (.)\n Log Out of the App (\)")
    option = input(" => ")
    if option == "!":

        print(f" Username: {dataOfUser[3]}\n Account Created: {dataOfUser[5]}")
        print(f" First Name: {dataOfUser[6]}\n Last Name: {dataOfUser[7]}")
        print(f" Birth Date: {dataOfUser[8]}")
        print(f" Would you like to go back to the main menu (A), or edit the information (B)?\n")
        userEdittingOption = input("Choose Option: ")
        validOption = False
        while not validOption:
            if userEdittingOption == "A":
                validOption = True
            elif userEdittingOption == "B":
                print("Which user detail would you like to change?\n")
                print("user_id\nemail_id\nusername\npassword\naccount_created\nfirst_name\nlast_name\nbirth_date\n")
                dataToAlter = input(" => ")

                # Validate the input to ensure that the correct user detail is updated
                dataToUpdate = ["user_id","email_id", "username", "password", "account_created", "first_name", "last_name", "birth_date"]
                while dataToAlter not in dataToUpdate:
                    dataToAlter = input("Invalid input, please enter one of the data options above: ")

                # New data is added to each table
                newData = input(f"Enter in new {dataToAlter}: ")
                print(f"UPDATE users SET username = {newData} WHERE inded_id = {dataOfUser[0]};")
                if dataToAlter == "user_id" and newData.isdigit():
                    cur.execute(f"UPDATE users SET user_id = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    cur.execute(f"UPDATE posts SET user_id = '{newData}' WHERE user_id = '{dataOfUser[1]}'")
                    cur.execute(f"UPDATE followers SET user_id = '{newData}' WHERE user_id = '{dataOfUser[1]}'")
                    cur.execute(f"UPDATE followers SET follow_id = '{newData}' WHERE follow_id = '{dataOfUser[1]}'")
                    validOption = True
                    conn.commit()
                elif dataToAlter == "email_id":
                    cur.execute(f"UPDATE users SET email_id = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    validOption = True
                    conn.commit()
                elif dataToAlter == "username":
                    cur.execute(f"UPDATE users SET username = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    validOption = True
                    givenUsername = newData
                    conn.commit()
                elif dataToAlter == "password":
                    cur.execute(f"UPDATE users SET password = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    validOption = True
                    givenPassword = newData
                    conn.commit()
                elif dataToAlter == "account_created":
                    cur.execute(f"UPDATE users SET account_created = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    validOption = True
                    conn.commit()
                elif dataToAlter == "first_name":
                    cur.execute(f"UPDATE users SET first_name = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    validOption = True
                    conn.commit()
                elif dataToAlter == "last_name":
                    cur.execute(f"UPDATE users SET last_name = '{newData}' WHERE index_id = '{dataOfUser[0]}'")
                    validOption = True
                    conn.commit()
                else:
                    print("Invalid Name Entered!")
            else:
                userEdittingOption = input("Invalid input: enter one of the options given above: ")

    elif option == "?":
        posts = cur.execute(f"SELECT post, posted_date FROM posts WHERE user_id = '{dataOfUser[1]}'").fetchall()

        print("List of your posts (by Date):\n")

        for tupleData in posts:
            print(f"User's Name: {nameOfUser}\nPost Date: '{tupleData[1]}'\nPost: '{tupleData[0]}'\n")

        print("Would you like to create a new post (1) or exit back to the main menu (2)?")
        postOption = input(" => ")

        validOption = False
        while validOption != True:
            if postOption == "1":
                newPostDate = input("Enter Post Date (MM/DD/YYYY): ")
                newPost = input("Enter Post: ")
                numberOfPostsData = cur.execute("SELECT max(index_id) FROM posts").fetchall()
                numberOfPostsOne = numberOfPostsData[0]
                numberOfPosts = 0 + numberOfPostsOne[0]
                cur.execute(f"INSERT INTO posts (index_id, user_id, post, posted_date) VALUES ('{numberOfPosts}', '{dataOfUser[1]}', '{newPost}', '{newPostDate}')")
                print("New post created!")
                validOption = True
            elif postOption == "2":
                print("Exiting...")
                validOption = True
            else:
                postOption = input("Invalid input, please re-enter either \"1\" or \"2\": ")

    elif option == ".":
        userFollowingData = cur.execute(f"SELECT followers.user_id, follow_id, first_name, last_name FROM followers INNER JOIN users ON followers.user_id = users.user_id WHERE follow_id = {dataOfUser[1]} UNION SELECT followers.user_id, follow_id, first_name, last_name FROM followers INNER JOIN users ON followers.follow_id = users.user_id WHERE followers.user_id = {dataOfUser[1]}").fetchall()
        allFollowerData = cur.execute("SELECT followers.user_id, follow_id, first_name, last_name FROM followers INNER JOIN users ON followers.follow_id = users.user_id").fetchall()
        peopleWhoUserFollows = cur.execute(f"SELECT user_id FROM followers WHERE follow_id = '{dataOfUser[1]}'").fetchall()

        print("People Who You Follow:")
        for followerData in userFollowingData:
            if followerData[1] == dataOfUser[1]:
                first = followerData[2]
                last = followerData[3]
                name = first + " " + last
                print(name)

        print("People Who Follow You:")
        for followerData in userFollowingData:
            if followerData[0] == dataOfUser[1]:
                first = followerData[2]
                last = followerData[3]
                name = first + " " + last
                print(name)

        print("Would you like to follow another person(A), or return to the main menu (B)?")
        validOption = False
        validUserID = True
        while not validOption:
            followOption = input(" => ")
            if followOption == "A":
                print("People Who You do not Follow:\n")

                # Collect a list of all the people in the following data
                peopleWhoUserDoesntFollow = [];
                for user in allFollowerData :
                    newUserToAdd = user[0]
                    mainUserID = dataOfUser[1]
                    if newUserToAdd not in peopleWhoUserDoesntFollow and newUserToAdd != mainUserID:
                        peopleWhoUserDoesntFollow.append(newUserToAdd)

                # Remove from the list each person who follows you
                for user in userFollowingData:
                    userToRemove = user[0]
                    if userToRemove in peopleWhoUserDoesntFollow:
                        peopleWhoUserDoesntFollow.remove(userToRemove)

                # Print the user_id's and names of all people who the user does not follow
                printedUserIDList = []
                for user in allFollowerData:
                    userID = user[0]
                    first = user[2]
                    last = user[3]
                    name = first + " " + last
                    if userID in peopleWhoUserDoesntFollow and not (userID in printedUserIDList):
                        printedUserIDList.append(userID)
                        print(f"({userID}): {name}\n")

                # Next, ask for the user_id of the person who they wish to follow
                personToFollow = input("Enter user_id of person you would like to follow: ")
                validOptionToFollow = False

                # Validate the input
                while not (int(personToFollow) in peopleWhoUserDoesntFollow):
                    personToFollow = input("Invalid input, please re-enter user_id of \nperson who you are not following: ")

                # Follow the person for the user
                numberOfFollowersData = cur.execute("SELECT max(index_id) FROM followers").fetchall()
                numberOfFollowersDataTuple = numberOfFollowersData[0]
                numberOfFollowers = 1 + numberOfFollowersDataTuple[0]
                cur.execute(f"INSERT INTO followers (index_id, user_id, follow_id) VALUES ('{numberOfFollowers}', '{personToFollow}', '{mainUserID}')")

                # Notify User of Completion
                print("New follower Added!")

                # Notify user which person they followed
                # for user in allFollowerData:
                #     userID = user[0]
                #     first = user[2]
                #     last = user[3]
                #     name = first + " " + last
                #     if userID == personToFollow:
                #         print(f"You are now following {name}!")

                # Correct boolean value to verify that the correct option was chosen
                validOption = True

            elif followOption == "B":
                print("Exiting...")
                validOption = True
            else:
                followOption = input("Invalid input, please enter a valid option from above: ")

    # Function to allow user to exit interface-loop
    elif option == "\\":
        print("Logging off, thank you for using Social Media Lite!")
        loggedIn = False

    # Option to ensure that the input is valid
    else:
        option = input("Invalid input, please select a valid option from above: ")

conn.commit()