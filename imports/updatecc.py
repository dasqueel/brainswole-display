from courseConcepts import *
from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts

courses = conceptsDb['courses'].find()

for course in courses:
	#print course['name']
	courseConcepts[course['name']] = course['concepts']