import psycopg2
import datetime



class DatabaseConnection:
	#Initialize FeestDatabaseConnection object
	#Creates a psycopg2 connection and cursor
	def __init__(self, dbName, dbUser, dbHost, dbPassword):
		#Concatenated string to connect to database
		dbConnect =  "dbname='" + dbName
		dbConnect += "' user='"+ dbUser 
		dbConnect += "' host='" + dbHost 
		dbConnect += "' password='" + dbPassword + "'"
		#Connecting to PostGresQL Database. Throws error if unable to connect
		#Connection is done outside of handler as global variable state is sometimes saved between function executions
		try:
		    self.conn = psycopg2.connect(dbConnect)
		except:
		    #TODO throw error here
		    print "I am unable to connect to the database"

		self.conn.rollback()

	def dbExecuteReturnNone(self, queryString, inputs=None):
		cur = self.conn.cursor()
		cur.execute(queryString, inputs)
		self.conn.commit()

	def dbExecuteReturnOne(self, queryString, inputs=None):
		cur = self.conn.cursor()
		cur.execute(queryString, inputs)
		self.conn.commit()
		return cur.fetchone()

	def dbExecuteReturnAll(self, queryString, inputs=None):
		cur = self.conn.cursor()
		cur.execute(queryString, inputs)
		self.conn.commit()
		return cur.fetchall()


	


