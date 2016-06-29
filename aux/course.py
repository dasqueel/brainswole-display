import sys
#sys.path.append('/Users/squeel/sites/brainswole/imports')
sys.path.append('/home/ubuntu/brainswole/imports')
from pymongo import MongoClient
from courseConcepts import *

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts

name = 'data structures'
concepts = courseConcepts[name]

doc = {'name':name,'concepts':concepts,'whyLinks':[]}

if conceptsDb['courses'].find_one({'name':name}):
	print name+' already added'
else:
	conceptsDb['courses'].insert(doc)
	print name+' added to courses!!'

'''
###add NEW course and its concepts to database
for courseName, concepts in courseConcepts.iteritems():
	if conceptsDb['courses'].find_one({'course':courseName}):
		pass
	else:
		#insert new courseDoc
		courseDoc = {'name':course['name']}
'''