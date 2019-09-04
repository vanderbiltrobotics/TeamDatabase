import psycopg2
import datetime
import database
import datetime

filename = 'dbcreds.txt' 
fileIn = open(filename,'r')

dbName = fileIn.readline().strip()
dbUser = fileIn.readline().strip()
dbHost = fileIn.readline().strip()
dbPassword = fileIn.readline().strip()


fileIn.close()


#Feest database object

fileIn.close()
db = database.DatabaseConnection(dbName, dbUser, dbHost, dbPassword)


#You are not commented
def getSwipe():
	card = ""
	while(len(card) != 20):
		card = input("Swipe your card: ")
		if(card.find('%E?') == 0):
			card = card[3:]
		if(card.find('+E?') == 20):
			card = card[:-3]

	return card

        

#Creates a prompt listing actions that users can take.
#Returns -1 for an exit command, or the number assoicated with the command
#Takes a list of options to provide
def listPrompt(options):
	i = 0
	strOut = ""
	for option in options:
		i = i + 1
		strOut += str(i) + ": " + option +"\n"
	strOut += "0: Exit\n"
	print(strOut)
	val = input("Make a selection: ")
	while(int(val) < 0 or int(val) > i):
		val = input("Invalid Input. Be smarter: ")
	return int(val)


#Registers users in database
def registerUserDB(cardID, name, subteam, subsystem, major, grade, email, phone):
	queryString = """
	INSERT INTO team_member (card_id, user_name, subteam, subsystem, major, grade, email, phone)
	VALUES 
	(%(card_id)s, %(user_name)s, %(subteam)s, %(subsystem)s, %(major)s, %(grade)s, %(email)s, %(phone)s)
	RETURNING card_id;"""
	inputs = {
		'card_id': cardID,
		'user_name' : name,
		'subteam' : subteam,
		'subsystem' : subsystem,
		'major' : major,
		'grade' : grade,
		'email': email,
		'phone' : phone
	}

	output = db.dbExecuteReturnOne(queryString, inputs)
	return output[0]


def getMajorsString():
	return "1: Mechanical Engineering\n2: Electrical Engineering\n3: Computer Engineering\n4: Computer Science\n5: Physics\n6: Math\n7: Engineering Science\n8: Biomedical Engineering"

def getSubteamString():
	return "1: Mechanical\n2: Electrical\n3: Programming"

def getSubsystemString():
	return "1: Frame and Drive\n2: Excavation\n3: Autonomy\n4: Power and Robot Controller"


#Provides the user interface to register a new user
def registerUserUI(cardID):
	print("Welcome to Swapnil's Super Sexy Sign-in Software System v3.14! I see that you have never signed-in before (maybe you should start coming to meetings).")
	print("Please enter your information in the following prompts. If you have previously registered, let Swapnil know that something is fucked up.")
	name = input("Full Name: ")
	grade = input("Year (1, 2, 3, or 4): ")
	email = input("Email: ")
	phone = input("Phone: ")

	print('\n')
	print(getMajorsString())
	major = input("Enter Major NUMBER : ")

	print('\n')
	print(getSubteamString())
	subteam = input("Enter Subteam NUMBER: ")

	print('\n')
	print(getSubsystemString())
	subsystem = input("Enter Subsystem NUMBER: ")

	userID = registerUserDB(cardID,name,subteam,subsystem,major,grade,email,phone)
	return (userID, name)

#Attempts to sign in a user. 
#If a user cannot be signed in, automatically calls registeredUserUI
def signInUserUI(cardID, meeting_id):
	queryString = """
	SELECT card_id, user_name 
	FROM team_member
	WHERE card_id = %(card_id)s
	LIMIT 1;"""

	inputs = { 'card_id' : cardID}

	output = db.dbExecuteReturnOne(queryString, inputs)
	if(not output):
		output = registerUserUI(cardID)

	#Checking if user has a meeting attendance entry.
	#This could occur in two situations. 
	# 1. Already signed in
	# 2. Provided excuse for being late or missing meeting
	queryStringCheckPreviousEntry = """
	SELECT time_in FROM meeting_attendance
	WHERE meeting_id = %(meeting_id)s AND member_id = %(member_id)s;"""

	inputsCheckPreviousEntry = {
		'meeting_id' : meeting_id,
		'member_id' : output[0]
	}

	previousAttendanceEntry = db.dbExecuteReturnOne(queryStringCheckPreviousEntry, inputsCheckPreviousEntry)
	#No entry has been previously recorded. Go ahead and insert a new one
	if(not previousAttendanceEntry):
		queryStringSignIn = """
		INSERT INTO meeting_attendance (meeting_id, member_id, time_in)
		VALUES
		(%(meeting_id)s, %(member_id)s, %(time_in)s);"""

		curTime = datetime.datetime.now().time()
		inputsSignIn = {
			"member_id" : output[0],
			"meeting_id" : meeting_id,
			"time_in" : curTime
		}
		db.dbExecuteReturnNone(queryStringSignIn, inputsSignIn)
		print("Hi " + output[1] + ", welcome to the meeting!")
	#Entry has been created, but no sign in time has been recorded. 
	# Probably because they told ahead of time that they were going to be late
	# Need to update the row to include the sign in time
	elif(previousAttendanceEntry[0] == None):
		queryStringSignIn = """
		UPDATE meeting_attendance
		SET time_in = %(time_in)s
		WHERE meeting_id = %(meeting_id)s AND member_id = %(member_id)s;"""

		curTime = datetime.datetime.now().time()
		inputsSignIn = {
			"member_id" : output[0],
			"meeting_id" : meeting_id,
			"time_in" : curTime
		}
		db.dbExecuteReturnNone(queryStringSignIn, inputsSignIn)
		print("Hi " + output[1] + ", welcome to the meeting!")

	else:
		print("You have already signed into this meeting, silly!")


#Attempts to sign in a user. 
#If a user cannot be signed in, automatically calls registeredUserUI
def signOutUserUI(cardID, meeting_id):
	queryString = """
	SELECT card_id, user_name 
	FROM team_member
	WHERE card_id = %(card_id)s
	LIMIT 1;"""

	inputs = { 'card_id' : cardID}

	output = db.dbExecuteReturnOne(queryString, inputs)

	#Checking if user has signed out already
	queryStringCheckPreviousEntry = """
	SELECT time_out FROM meeting_attendance
	WHERE meeting_id = %(meeting_id)s AND member_id = %(member_id)s;"""

	inputsCheckPreviousEntry = {
		'meeting_id' : meeting_id,
		'member_id' : output[0]
	}

	previousAttendanceEntry = db.dbExecuteReturnOne(queryStringCheckPreviousEntry, inputsCheckPreviousEntry)
	#Entry has been created, but no sign out time has been recorded. 
	# Need to sign out user
	if(previousAttendanceEntry[0] == None):
		queryStringSignIn = """
		UPDATE meeting_attendance
		SET time_out = %(time_out)s
		WHERE meeting_id = %(meeting_id)s AND member_id = %(member_id)s;"""

		curTime = datetime.datetime.now().time()
		inputsSignIn = {
			"member_id" : output[0],
			"meeting_id" : meeting_id,
			"time_out" : curTime
		}
		db.dbExecuteReturnNone(queryStringSignIn, inputsSignIn)
		print("Thanks for signing out! I'll miss you :(")

	else:
		print("You have already signed out of this meeting, silly! Get outta here")


#Function to create a new meeting. 
#May want to add functionality in the future to ingest file containing meetings for ease
def createMeetingUI():
	#Getting and formatting inputs
	date = input("Enter Meeting Date (MM/DD): ").replace(' ','')
	startTime = input("Enter meeting start time (HH:MM) (24-hour time): ").replace(' ','')
	endTime = input("Enter meeting end time (HH:MM) (24-hour time): ").replace(' ','')
	date += "/" + str(datetime.datetime.now().year)
	startTime += ":00"
	endTime += ":00"

	#Query to insert new meeting into database
	queryString = """
	INSERT INTO meeting (meeting_date, start_time, end_time)
	VALUES
	(%(meeting_date)s, %(start_time)s, %(end_time)s)
	RETURNING meeting_id;"""

	inputs = {
		'meeting_date' : date,
		'start_time' : startTime,
		'end_time' : endTime
	}

	return db.dbExecuteReturnOne(queryString, inputs)[0]

#Returns a list of strings containing the start and end times of meeting today
def getMeetingsToday():
	date = datetime.datetime.now().date()
	queryString = """
	SELECT start_time, end_time, meeting_id
	FROM meeting
	WHERE meeting_date = %(date)s;"""

	inputs = { 'date' : date}
	output = []
	meetingIds = []
	meetings = db.dbExecuteReturnAll(queryString, inputs)
	for meeting in meetings:
		output.append(meeting[0].strftime("%H:%M") + " - "  + meeting[1].strftime("%H:%M"))
		meetingIds.append(meeting[2])
	return output, meetingIds

#Returns a list of strings containing the start time, end time, and dates for all meetings
def getMeetingsAll():
	queryString = """
	SELECT meeting_date, start_time, end_time, meeting_id
	FROM meeting;"""

	output = []
	meetingIds = []
	meetings = db.dbExecuteReturnAll(queryString)
	for meeting in meetings:
		output.append(meeting[0].strftime("%m/%d") + ": " + meeting[1].strftime("%H:%M") + " - "  + meeting[2].strftime("%H:%M"))
		meetingIds.append(meeting[3])

	return output, meetingIds

#Retrieves user id and user name from database based on name
# Can retrieve users by portion of name at beginning, in middle, or at end of name string
def getUsersByName(nameIn):
	nameIn = "%" + nameIn + "%"
	queryString = """
	SELECT card_id, user_name
	FROM team_member
	WHERE user_name LIKE %(nameIn)s;"""
	inputs = {
		'nameIn' : nameIn
	}

	userNames = []
	userIds = []
	users = db.dbExecuteReturnAll(queryString, inputs)
	for user in users:
		userIds.append(user[0])
		userNames.append(user[1])

	return userIds,userNames

# Generates a list of emails of all of users who attended specified meeting
def getMeetingAttendance(meetingId):
	queryString = """
	SELECT team_member.email
	FROM meeting_attendance
	INNER JOIN team_member ON meeting_attendance.member_id = team_member.card_id
	WHERE meeting_attendance.meeting_id = %(meetingId)s AND meeting_attendance.time_in IS NOT NULL;"""
	inputs = {
		'meetingId' : meetingId
	}
	emails = ""
	output = db.dbExecuteReturnAll(queryString, inputs)
	for user in output:
		emails += user[0] + "\n"

	return emails


#BEGIN PROGRAM EXECUTION -------------------------------------------------------------------------------------------------------
while(True):
	print("Welcome to Swapnil's Super Sexy Sign-in Software System v3.14! Choose one of the options below to get started.")
	selection = listPrompt(["Sign-in Users", "Sign-out Users" , "Create Meeting", "Get Meeting Stats", "Add Excused Absence"])

	#SIGN IN USERS
	if(selection == 1):
		meeting = 0
		#Retrieving Meetings and respective IDs
		meetings, meetingsIds = getMeetingsToday()
		#Prompting the user to make a selection for meeting
		meetingSelection = listPrompt(meetings)
		if(meetingSelection != 0):
			meeting = meetingsIds[meetingSelection - 1]

		while(True):
			print('\n')
			print('\n')
			card = getSwipe()
			signInUserUI(card, meeting)
	
	#SIGN OUT USERS
	if(selection == 2):
		meeting = 0
		#Retrieving Meetings and respective IDs
		meetings, meetingsIds = getMeetingsToday()
		#Prompting the user to make a selection for meeting
		meetingSelection = listPrompt(meetings)
		if(meetingSelection != 0):
			meeting = meetingsIds[meetingSelection - 1]

		while(True):
			print('\n')
			print('\n')
			card = getSwipe()
			signOutUserUI(card, meeting)
	#CREATE A NEW MEETING
	if(selection == 3):
		
		createMeetingUI()

	#GET MEETING STATS
	if(selection == 4):
		meeting = 0
		#Retrieving Meetings and respective IDs
		meetings, meetingsIds = getMeetingsAll()
		#Prompting the user to make a selection for meeting
		meetingSelection = listPrompt(meetings)
		if(meetingSelection != 0):
			meeting = meetingsIds[meetingSelection - 1]
		print(getMeetingAttendance(meeting))




