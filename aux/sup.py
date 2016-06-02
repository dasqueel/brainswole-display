from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.Users
generalDb = client.Cerebral

#remove user from database
userName = "seantaylor"
email = "taylor@miami.edu"

userNameEmail = {"userName":userName,"email":email}

generalDb['general'].update({"doc":"general"},{"$pull":{"registeredEmails":email,"registeredUserNames":userName,"userNameEmail":userNameEmail}})
userDb[userName].drop()