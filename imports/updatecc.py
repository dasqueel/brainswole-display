###update existing courses with their new concepts

from courseConcepts import *
from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts

courses = conceptsDb['courses'].find()

for course in courses:
	course['concepts'] = courseConcepts[course['name']]
	conceptsDb['courses'].update({'name':course['name']},{'$set':{'concepts':courseConcepts[course['name']]}})